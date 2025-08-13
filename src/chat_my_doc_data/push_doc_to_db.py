import polars as pl
from loguru import logger
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

def load_reviews_data() -> pl.DataFrame:
    """
    Load the IMDB reviews data from a Parquet file.
    """
    df = pl.read_parquet("gs://rag-open-data/imdb/standard/imdb_reviews.parquet")
    logger.info(f"Loaded {df.shape[0]} reviews from the dataset.")
    
    return df


def encode_reviews(
    df: pl.DataFrame,
    col_to_encode: str,
    encoder: SentenceTransformer
) -> pl.DataFrame:
    logger.info(f"Encoding column '{col_to_encode}' using the SentenceTransformer model.")

    df = df.with_columns(
        pl.lit(encoder.encode(df[col_to_encode].to_list()))
        .alias("vector")
    )
    
    logger.info(f"Encoded {df.shape[0]} reviews.")
    
    return df

def add_index(df: pl.DataFrame, index_col: str) -> pl.DataFrame:
    """
    Add an index column to the DataFrame based on the specified index column.
    """
    return df.with_row_index(index_col)
    
class Qdrant:
    def __init__(self, url: str):
        self.client = QdrantClient(url=url)
        
    def _if_collection_exists(self, collection_name:str) -> bool:
        collections=self.client.get_collections()
        collection_exists = (
            collection_name
            in [col.name for col in collections.collections]
        )
        
        return collection_exists
    
    def setup_collection(
        self,
        collection_name: str,
        vectors_size: int | None = None,
        distance: models.Distance = models.Distance.COSINE
    ) -> None:
        """
        Set up a collection in Qdrant with the specified parameters.
        """
        if self._if_collection_exists(collection_name):
            self.collection_name = collection_name
            logger.info(f"Used Collection '{collection_name}'.")
            return
        else:
            logger.info(f"Collection '{collection_name}' does not exist. Creating a new collection.")

            if vectors_size is None:
                raise ValueError("vectors_size must be specified if the collection does not exist.")

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vectors_size,
                    distance=distance,
                ),
            )
            logger.info(f"Created Collection '{collection_name}' with vectors size {vectors_size} and distance {distance}.")
            self.collection_name = collection_name
    
    def upload_documents(
        self,
        df: pl.DataFrame,
        vectors_column: str,
        id_column: str,
        payload_columns: list
    ) -> None:  
        """Upload documents to the Qdrant collection.
        """
        if not self.collection_name:
            raise ValueError("Collection name is not set. Please call setup_collection() first.")

        self.client.upload_collection(
            collection_name="imdb_reviews",
            ids=df[id_column].to_list(),
            payload=df[payload_columns].to_dicts(),
            vectors=df[vectors_column].to_list()
        )

def main():
    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    
    df = load_reviews_data()
    df = encode_reviews(
        df,
        col_to_encode="review",
        encoder=encoder
    )
    df = add_index(df, "id")
    
    db = Qdrant(url="http://34.87.227.185:6333")
    
    db.setup_collection(
        collection_name="imdb_reviews",
        vectors_size=encoder.get_sentence_embedding_dimension(),
        distance=models.Distance.COSINE,
    )
    
    db.upload_documents(
        df,
        vectors_column="vector",
        id_column="id",
        payload_columns=[
            'review_title',
            'review_rating',
            'review',
            'title',
            'rating',
            'genre',
            'year'
        ]
    )
    
    logger.info("Documents uploaded successfully to Qdrant collection 'imdb_reviews'.")
    

if __name__ == "__main__":
    main()
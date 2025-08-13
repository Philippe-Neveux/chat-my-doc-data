from pathlib import Path
from typing import Literal, Optional

import polars as pl
import typer
from google.cloud import storage
from loguru import logger


def load_imdb_data(
    blob_name_list: str = "gs://rag-open-data/imdb/raw/IMDB_List.csv",
    blob_name_reviews: str = "gs://rag-open-data/imdb/raw/IMDB_Reviews.csv"
) -> pl.DataFrame:
    """
    Load and join IMDB list and reviews data from GCS.

    Args:
        blob_name_list: GCS path to the IMDB list CSV file
        blob_name_reviews: GCS path to the IMDB reviews CSV file

    Returns:
        Combined dataframe with reviews joined to movie list
    """
    df_list = pl.read_csv(blob_name_list)
    df_reviews = pl.read_csv(blob_name_reviews)

    df = (
        df_reviews
        .join(
            df_list,
            left_on="imdb_id",
            right_on="id",
            how="left"
        )
    )

    return df

def transform_imdb_data(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .drop("")
        .rename({
            "review title": "review_title"
        })
    )

def save_to_parquet(
    df: pl.DataFrame,
    output_path: str,
    compression: Literal["lz4", "uncompressed", "snappy", "gzip", "lzo", "brotli", "zstd"] = "snappy"
) -> None:
    """
    Save dataframe to parquet format.

    Args:

        df: Polars dataframe to save
        output_path: Output file path
        compression: Compression type (snappy, gzip, lz4, zstd)
    """
    # Create directory if it doesn't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    df.write_parquet(output_path, compression=compression)


def upload_to_gcs(
    local_file_path: str,
    bucket_name: str,
    blob_name_output: str,
    project_id: Optional[str] = None
) -> None:
    """
    Upload a file to Google Cloud Storage.
    
    Args:
        local_file_path: Path to the local file to upload
        bucket_name: Name of the GCS bucket
        blob_name_output: Name of the blob in the bucket
        project_id: GCP project ID (optional, uses default if not provided)
    """
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name_output)
    
    blob.upload_from_filename(local_file_path)
    logger.success(f"Uploaded {local_file_path} to gs://{bucket_name}/{blob_name_output}")


app = typer.Typer()


@app.command()
def process_imdb_data(
    project_id: Optional[str] = typer.Option("gen-ai-466406", help="GCP project ID"),
    bucket_name: Optional[str] = typer.Option("rag-open-data", help="GCS bucket name for upload"),
    output_file: Optional[str] = typer.Option("data/standard/imdb_reviews.parquet", help="Output parquet file path"),
    blob_name_output: Optional[str] = typer.Option("imdb/standard/imdb_reviews.parquet", help="GCS blob name"),
    compression: Optional[str] = typer.Option("snappy", help="Compression type for parquet file")
) -> None:
    """Process IMDB data: load, transform, save to parquet format, and optionally upload to GCS."""

    df = load_imdb_data(
        blob_name_list="gs://rag-open-data/imdb/raw/IMDB_List.csv",
        blob_name_reviews="gs://rag-open-data/imdb/raw/IMDB_Reviews.csv"
    )
    df = transform_imdb_data(df)

    logger.info(f"Saving processed data to {output_file}")
    save_to_parquet(df, output_file, compression)

    logger.success(f"Successfully processed {len(df)} records")
    
    # Upload to GCS if bucket name is provided
    if bucket_name:
        blob_path = blob_name_output or Path(output_file).name
        logger.info(f"Uploading to GCS bucket: {bucket_name}")
        upload_to_gcs(output_file, bucket_name, blob_path, project_id)


if __name__ == "__main__":
    app()

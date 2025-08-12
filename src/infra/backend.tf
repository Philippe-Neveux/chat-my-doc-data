terraform {
  backend "gcs" {
    bucket = "gen-ai-466406-tfstate"
    prefix = "terraform-qdrant/state"
  }
}
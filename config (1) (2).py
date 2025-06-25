import os
from dotenv import load_dotenv

load_dotenv()
BLOB_URL = os.getenv("Blob_URL")  # Base URL for your Azure Blob Storage
BLOB_TOKEN = os.getenv("Blob_Token")  # SAS Token or Connection String
CONTAINER_NAME = "blob"  # Change this to your container name
COSMOS_DB_URL = os.getenv("AZURE_COSMOSDB_ENDPOINT")
COSMOS_DB_KEY = os.getenv("AZURE_COSMOSDB_KEY")
DATABASE_NAME = "asd"
CONTAINER_NAME = "vectors"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
import fitz  # PyMuPDF for extracting text from PDF
import openai
import tiktoken
from azure.cosmos import CosmosClient
import json
import os
import uuid
from config import (
    COSMOS_DB_URL,
    COSMOS_DB_KEY,
    DATABASE_NAME,
    CONTAINER_NAME,
    OPENAI_API_KEY,
)

# 🔹 Load environment variables
# 🔹 Initialize CosmosDB client
client = CosmosClient(COSMOS_DB_URL, COSMOS_DB_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

openai.api_key = OPENAI_API_KEY

# 🔹 Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
    return text.strip()

# 🔹 Function to split text into chunks (optimized size: 300-500 tokens)
def split_text(text, chunk_size=500):
    encoding = tiktoken.get_encoding("cl100k_base")  # Correct encoding for OpenAI
    tokens = encoding.encode(text)

    chunks = []
    for i in range(0, len(tokens), chunk_size):
        chunk = tokens[i : i + chunk_size]  # Take a slice of max 500 tokens
        chunks.append(encoding.decode(chunk))  # Convert back to text

    return chunks

# 🔹 Function to generate vector embeddings
# 🔹 Function to generate vector embeddings
def generate_embeddings(text_chunks):
    embeddings = []
    for i, chunk in enumerate(text_chunks):
        try:
            response = openai.embeddings.create(  # ✅ Corrected function
                model="text-embedding-ada-002",  
                input=[chunk]  # ✅ Input must be a list
            )
            embeddings.append(response.data[0].embedding)  # ✅ Corrected response format
        except Exception as e:
            print(f"❌ Error generating embeddings for chunk {i}: {e}")
    return embeddings

# 🔹 Function to store vectors in CosmosDB
# 🔹 Function to store vectors in CosmosDB
def store_vectors_in_cosmos(file_name, text_chunks, vectors):
    if not vectors:
        print("No vectors to store.")
        return

    for i in range(len(text_chunks)):
        doc_id = str(uuid.uuid4())  # Unique ID for each chunk

        item = {
            "id": doc_id,
            "file_name": file_name,
            "chunk_index": i,  # ✅ Add index for tracking order
            "text": text_chunks[i],
            "vector": vectors[i],
        }

        try:
            container.upsert_item(item)  # ✅ Store each chunk as a separate document
            print(f"✅ Stored chunk {i+1}/{len(text_chunks)} in CosmosDB")
        except Exception as e:
            print(f"❌ Error storing chunk {i+1}: {e}")

# 🔹 Main function
def process_pdf_and_store(pdf_path):
    file_name = os.path.basename(pdf_path)
    text = extract_text_from_pdf(pdf_path)

    if not text:
        print("❌ No text extracted from the document.")
        return

    text_chunks = split_text(text)  # Split text into smaller chunks
    vectors = generate_embeddings(text_chunks)  # Generate embeddings for each chunk
    store_vectors_in_cosmos(file_name, text_chunks, vectors)

# 🔹 Run the script
if __name__ == "__main__":
    pdf_path = "narcotic-drugs-and-psychotropic-substances-act-1985.pdf"  # Change this to your actual PDF path
    process_pdf_and_store(pdf_path)

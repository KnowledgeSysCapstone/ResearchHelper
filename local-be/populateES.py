import os
import json
from elasticsearch import Elasticsearch

# Get API key from environment variable.
API_KEY = os.getenv("ES_LOCAL_API_KEY")
if not API_KEY:
    raise ValueError("Missing ES_LOCAL_API_KEY environment variable.")

# Endpoint for ES, index name, data folder.
ES_ENDPOINT = "https://..."
INDEX_NAME = "test_index"
FOLDER_PATH = "../es_data"

# Initialize Elasticsearch client
client = Elasticsearch(ES_ENDPOINT, api_key=API_KEY)

# Create index if it doesn't exist
if not client.indices.exists(index=INDEX_NAME):
    client.indices.create(index=INDEX_NAME)

# Iterate over files in the specified folder
for filename in os.listdir(FOLDER_PATH):
    file_path = os.path.join(FOLDER_PATH, filename)
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            doc = {"filename": filename, "content": content}
            client.index(index=INDEX_NAME, document=doc)
            print(f"Indexed {filename}")

print("Indexing complete.")
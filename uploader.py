import json
import requests
import os
import numpy as np
from elasticsearch import Elasticsearch
from tqdm import tqdm
import collect_documents as cdocs

# Get environment variables.
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('ELASTIC_PASSWORD='):
            elastic_password = line.strip().split('=')[1]
            break

# Configure Elasticsearch connection with basic authentication (default user, password).
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", elastic_password)
)

# Check if Elasticsearch is running.
try:
    es.info()
    print("Successfully connected to Elasticsearch")
except Exception as e:
    print(f"Unable to connect to Elasticsearch: {e}")
    exit(1)

index_name = "research_papers"
# Create index if it doesn't exist.
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=cdocs.elasticsearch_mappings())
    print("Created 'research_papers' index.")
else:
    doc_count = es.cat.count(index=index_name, format="json")[0]['count']
    print(f"Number of documents in index {index_name}: {doc_count}.")

# Gather documents.
print("Gathering documents...")
docs = cdocs.get_documents("food", 1000, 100, do_print=True)

# Upload data to Elasticsearch.
print("Uploading data to Elasticsearch...")
bulk_data = []
for doc in tqdm(docs, desc="Indexing documents"):
    # Prepare bulk data for Elasticsearch.
    bulk_data.append({"index": {"_index": index_name}})
    bulk_data.append(doc)

    # Submit in batches of 200 documents to avoid losing too much progress.
    if len(bulk_data) >= 200:
        es.bulk(body=bulk_data)
        bulk_data = []

# Submit remaining data.
if bulk_data:
    es.bulk(body=bulk_data)

print("Complete! Data successfully uploaded to Elasticsearch.")

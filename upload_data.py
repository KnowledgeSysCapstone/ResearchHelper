import json
import requests
import os
import numpy as np
from elasticsearch import Elasticsearch
from tqdm import tqdm

# Get environment variables
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('ELASTIC_PASSWORD='):
            elastic_password = line.strip().split('=')[1]
            break

# Configure Elasticsearch connection
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", elastic_password)
)

# Check if Elasticsearch is running
try:
    es.info()
    print("Successfully connected to Elasticsearch")
except Exception as e:
    print(f"Unable to connect to Elasticsearch: {e}")
    exit(1)

# Create index if it doesn't exist
if not es.indices.exists(index="research_papers"):
    mapping = {
        "mappings": {
            "properties": {
                "doi": {"type": "keyword"},
                "sentences": {"type": "text"},
                "sentence_vectors": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }
    es.indices.create(index="research_papers", body=mapping)
    print("Created 'research_papers' index")

# Load original text data
print("Loading original text data...")
with open('abstracts_parsed.txt', 'r') as f:
    data = f.read().strip()
    # Remove any trailing percentage sign
    if data.endswith('%'):
        data = data[:-1]
    parsed_data = json.loads(data)

# Load vectorized data
print("Loading vectorized data...")
try:
    with open('abstracts_vectorized.txt', 'r') as f:
        data = f.read().strip()
        if data.endswith('%'):
            data = data[:-1]
        vectorized_data = json.loads(data)
        print(f"Successfully loaded vectorized data")
except json.JSONDecodeError as e:
    print(f"JSON parsing error: {e}")
    print("Trying line-by-line parsing method...")
    
    # If JSON parsing fails, try manual parsing
    vectorized_data = {}
    current_doi = None
    current_vectors = []
    bracket_count = 0
    combined_lines = ""
    
    with open('abstracts_vectorized.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Count brackets to track JSON structure
            bracket_count += line.count('{') - line.count('}')
            bracket_count += line.count('[') - line.count(']')
            
            combined_lines += line
            
            # When brackets are balanced, try to parse complete JSON object
            if bracket_count == 0 and combined_lines.strip():
                try:
                    obj = json.loads(combined_lines)
                    vectorized_data = obj
                    combined_lines = ""
                    print("Successfully parsed complete JSON object")
                    break
                except json.JSONDecodeError:
                    # Might not be complete JSON, continue adding lines
                    pass

print(f"Parsed original text for {len(parsed_data)} DOIs")
print(f"Parsed vector data for {len(vectorized_data)} DOIs")

# Upload data to Elasticsearch
print("Uploading data to Elasticsearch...")
bulk_data = []
count = 0

for doi, sentences in tqdm(parsed_data.items()):
    if doi in vectorized_data:
        vectors = vectorized_data[doi]
        # Ensure sentence and vector counts match
        min_len = min(len(sentences), len(vectors))
        
        for i in range(min_len):
            # Prepare document
            doc = {
                "doi": doi,
                "sentences": sentences[i],
                "sentence_vectors": vectors[i]
            }
            
            # Prepare bulk operation
            bulk_data.append({"index": {"_index": "research_papers"}})
            bulk_data.append(doc)
            count += 1
            
            # Submit in batches of 2000 documents
            if len(bulk_data) >= 4000:
                print(f"Bulk uploading {len(bulk_data)//2} documents...")
                try:
                    es.bulk(body=bulk_data)
                    print(f"Uploaded {count} documents")
                except Exception as e:
                    print(f"Error during upload: {e}")
                bulk_data = []

# Submit remaining data
if bulk_data:
    print(f"Uploading remaining {len(bulk_data)//2} documents...")
    try:
        es.bulk(body=bulk_data)
        print(f"Total {count} documents uploaded")
    except Exception as e:
        print(f"Error uploading remaining data: {e}")

print("Complete! Data successfully uploaded to Elasticsearch.") 
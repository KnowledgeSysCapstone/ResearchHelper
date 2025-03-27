# Research Helper - Vector Search System

A vector search system based on Elasticsearch for finding similar sentences in research papers using vector similarity.

## System Architecture

- **Elasticsearch**: Provides vector storage and search functionality
- **FastAPI Backend**: Provides vectorization and search APIs
- **Next.js Frontend**: Provides user interface

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Node.js 18+

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ResearchHelper.git
   cd ResearchHelper
   ```

2. Create `.env` file with the following content:
   ```
   STACK_VERSION=8.12.0
   ELASTIC_PASSWORD=yourpassword
   ES_PORT=9200
   KIBANA_PORT=5601
   MEM_LIMIT=1g
   ```

## Starting the Services

Start all services using Docker Compose:

```bash
docker-compose up --build
```

After startup, you can access the following services:

- Elasticsearch: http://localhost:9200
- FastAPI backend: http://localhost:8000
- Next.js frontend: http://localhost:3000

## Creating Elasticsearch Index

The system will automatically create the required index when uploading data, but you can also create it manually:

```bash
curl -XPUT -u elastic:yourpassword "http://localhost:9200/research_papers" \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": {
      "properties": {
        "doi": {
          "type": "keyword"
        },
        "sentences": {
          "type": "text"
        },
        "sentence_vectors": {
          "type": "dense_vector",
          "dims": 384,
          "index": true,
          "similarity": "cosine"
        }
      }
    }
  }'
```

## Data Preparation and Upload

The system requires two key files:

- `abstracts_parsed.txt`: Contains original sentence data indexed by DOI
- `abstracts_vectorized.txt`: Contains vector representations of sentences

### Data Format

1. **abstracts_parsed.txt**: A JSON file with DOIs as keys and arrays of sentences as values
   ```json
   {
     "10.1234/example": ["First sentence.", "Second sentence."],
     "10.5678/sample": ["Another paper sentence."]
   }
   ```

2. **abstracts_vectorized.txt**: A JSON file with DOIs as keys and arrays of vector arrays as values
   ```json
   {
     "10.1234/example": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
     "10.5678/sample": [[0.5, 0.6, ...]]
   }
   ```

### Uploading Data

To upload data to Elasticsearch, run:

```bash
python upload_data.py
```

The script will:
1. Connect to Elasticsearch
2. Create the index if it doesn't exist
3. Parse the data files
4. Upload documents in batches
5. Report progress and completion

## Using the System

1. Visit the frontend interface: http://localhost:3000
2. Enter your search text in the search box
3. The system will convert the text to a vector and find the most similar sentences
4. View the search results, including DOI, similarity score, and sentence content

## API Endpoints

The backend provides the following API endpoints:

- **Vector Search**: `POST /search/vector` - Search for similar sentences by text
- **DOI Search**: `GET /search/doi/{doi}` - Find sentences by DOI
- **Health Check**: `GET /health` - Check system status

## Troubleshooting

- **Elasticsearch Connection Issues**: Check if Elasticsearch is running with `curl -u elastic:yourpassword http://localhost:9200`
- **Backend Issues**: Check logs with `docker logs fastapi_backend`
- **Frontend Issues**: Check logs with `docker logs nextjs_frontend`
- **Data Loading Issues**: Verify file formats and run `upload_data.py` with proper permissions

## Clearing and Rebuilding the Index

To clear the index and reupload data:

```bash
# Delete the index
curl -XDELETE -u elastic:yourpassword "http://localhost:9200/research_papers"

# Recreate the index
curl -XPUT -u elastic:yourpassword "http://localhost:9200/research_papers" -H "Content-Type: application/json" -d '{"mappings":{"properties":{"doi":{"type":"keyword"},"sentences":{"type":"text"},"sentence_vectors":{"type":"dense_vector","dims":384,"index":true,"similarity":"cosine"}}}}'

# Reupload data
python upload_data.py
```
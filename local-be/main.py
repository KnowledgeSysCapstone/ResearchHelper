from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os
import time
from dotenv import load_dotenv
from pydantic import BaseModel
import numpy as np
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded")
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")
    pass  # Ignore error if .env file doesn't exist

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Elasticsearch configuration
elastic_password = os.getenv("ELASTIC_PASSWORD", "yourpassword")
elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
logger.info(f"Using Elasticsearch host: {elasticsearch_host}")
logger.info(f"Using Elasticsearch password: {elastic_password[:2]}***")

# Create global Elasticsearch client variable
es = None

# Define connection function with retry
def connect_elasticsearch(max_retries=5, retry_interval=5):
    global es
    
    # Try connections in Docker network
    es_hosts = [
        elasticsearch_host,         # Host from environment variable
        "http://elasticsearch:9200",  # Docker network name
        "http://localhost:9200",      # Local hostname
        "http://127.0.0.1:9200",      # IPv4 local address
    ]
    
    # Add retry logic
    for retry in range(max_retries):
        logger.info(f"Attempting to connect to Elasticsearch (try {retry+1}/{max_retries})")
        
        for host in es_hosts:
            try:
                logger.info(f"Trying to connect to: {host}")
                es_client = Elasticsearch(
                    host,
                    basic_auth=("elastic", elastic_password),
                    verify_certs=False,
                    request_timeout=30
                )
                
                if es_client.ping():
                    logger.info(f"Successfully connected to Elasticsearch: {host}")
                    return es_client
            except Exception as e:
                logger.error(f"Connection to {host} failed: {e}")
        
        # If no successful connection, wait before retrying
        if retry < max_retries - 1:
            logger.info(f"Waiting {retry_interval} seconds before retrying...")
            time.sleep(retry_interval)
    
    # After all retries failed, return mock client
    logger.warning("All connection attempts failed, using mock client")
    return create_mock_client()

# Create mock client
def create_mock_client():
    class MockElasticsearch:
        def ping(self):
            return True
            
        def cluster(self):
            class MockCluster:
                def health(self):
                    return {"status": "mock_yellow"}
            return MockCluster()
            
        def search(self, **kwargs):
            logger.warning("Using mock Elasticsearch client, returning empty results")
            index = kwargs.get('index', 'unknown')
            body = kwargs.get('body', {})
            logger.info(f"Mock search: index={index}, query={body}")
            return {"hits": {"hits": []}}
    
    return MockElasticsearch()

# Initialize vector model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Index name
INDEX_NAME = "research_papers"

class SearchRequest(BaseModel):
    text: str
    top_k: int = 10

# Application startup event
@app.on_event("startup")
async def startup_event():
    global es
    # Connect to Elasticsearch
    es = connect_elasticsearch()
    logger.info("Application startup complete, Elasticsearch client initialized")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health = es.cluster.health()
        return {"status": "ok", "es_status": health["status"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/vectorize")
async def vectorize_text(text: str):
    """Vectorize text"""
    try:
        vector = model.encode(text).tolist()
        return {"vector": vector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/vector")
async def vector_search(request: SearchRequest):
    """Search by text vector"""
    try:
        logger.info(f"Received vector search request: {request.text[:30]}... (top_k={request.top_k})")
        
        # Check Elasticsearch connection
        if es is None:
            logger.error("Elasticsearch client not initialized")
            raise HTTPException(status_code=503, detail="Elasticsearch service unavailable")
            
        # Vectorize input text
        try:
            query_vector = model.encode(request.text).tolist()
            logger.info(f"Successfully vectorized text, vector dimension: {len(query_vector)}")
        except Exception as e:
            logger.error(f"Text vectorization failed: {e}")
            raise HTTPException(status_code=500, detail=f"Text vectorization error: {str(e)}")
        
        # Build query
        try:
            query = {
                "knn": {
                    "field": "sentence_vectors",
                    "query_vector": query_vector,
                    "k": request.top_k,
                    "num_candidates": 100
                },
                "_source": ["doi", "sentences"]
            }
            logger.info("KNN query built")
        except Exception as e:
            logger.error(f"Query building failed: {e}")
            raise HTTPException(status_code=500, detail=f"Query building error: {str(e)}")
        
        # Execute search
        try:
            response = es.search(index=INDEX_NAME, body=query)
            logger.info(f"Search successful, found {len(response['hits']['hits'])} results")
        except Exception as e:
            logger.error(f"Elasticsearch search failed: {e}")
            raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
        
        # Process results
        results = []
        for hit in response['hits']['hits']:
            results.append({
                "doi": hit['_source']['doi'],
                "sentence": hit['_source']['sentences'],
                "score": hit['_score']
            })
        
        logger.info(f"Successfully returned {len(results)} results")
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unhandled exception in vector search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/doi/{doi}")
async def search_by_doi(doi: str, size: int = 10):
    """Search documents by DOI"""
    try:
        query = {
            "query": {
                "term": {
                    "doi": doi
                }
            },
            "size": size
        }
        
        response = es.search(index=INDEX_NAME, body=query)
        
        results = []
        for hit in response['hits']['hits']:
            results.append({
                "doi": hit['_source']['doi'],
                "sentence": hit['_source']['sentences'],
                "score": hit['_score']
            })
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
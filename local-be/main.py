from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

# Load .env if available.
load_dotenv()

app = FastAPI()

# Allow frontend access.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables.
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "password")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")

# Initialize elasticsearch connection and sentence vector model.
es = Elasticsearch(ELASTICSEARCH_HOST, basic_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Placeholder Index (.env variable?)
INDEX_NAME = "research_papers"

# Request Schema for Vector Search
class SearchRequest(BaseModel):
    text: str
    top_k: int = 10

@app.post("/search/vector")
async def vector_search(request: SearchRequest):
    try:
        query_vector = model.encode(request.text).tolist()
        query = {
            "knn": {
                "field": "sentence_vectors",
                "query_vector": query_vector,
                "k": request.top_k,
                "num_candidates": 100
            },
            "_source": ["doi", "sentences"]
        }
        response = es.search(index=INDEX_NAME, body=query)
        results = [
            {
                "doi": hit["_source"]["doi"],
                "sentence": hit["_source"]["sentences"],
                "score": hit["_score"]
            } for hit in response["hits"]["hits"]
        ]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/doi/{doi}")
async def search_by_doi(doi: str, size: int = 10):
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
        results = [
            {
                "doi": hit["_source"]["doi"],
                "sentence": hit["_source"]["sentences"],
                "score": hit["_score"]
            } for hit in response["hits"]["hits"]
        ]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

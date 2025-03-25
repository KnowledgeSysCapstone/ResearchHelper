from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch

app = FastAPI()

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "documents"

@app.post("/index/")
async def index_document(doc_id: str, content: str):
    """Indexes a document in Elasticsearch."""
    try:
        response = es.index(index=INDEX_NAME, id=doc_id, body={"content": content})
        return {"result": response["result"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/")
async def search_documents(query: str):
    """Searches for documents matching the query."""
    try:
        response = es.search(index=INDEX_NAME, body={"query": {"match": {"content": query}}})
        return {"hits": response["hits"]["hits"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
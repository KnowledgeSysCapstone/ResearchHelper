from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
from collect_documents import form_query

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

# Initialize elasticsearch connection.
es = Elasticsearch(ELASTICSEARCH_HOST, basic_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)

# Placeholder Index (.env variable?).
INDEX_NAME = "research_papers"

# Request schema for vector search.
class SearchRequest(BaseModel):
    text: str
    top_k: int = 10

# Copy of below, utilized to test raw hit format from ES.
@app.post("/search/vector/test")
async def vector_search_test(request: SearchRequest):
    try:
        query = form_query(request.text, request.top_k)
        response = es.search(index=INDEX_NAME, body=query)
        if response["hits"]["hits"]:
            first_hit = response["hits"]["hits"][0]
            print("First Elasticsearch hit:\n", first_hit)
            return {"raw_first_hit": first_hit}
        else:
            return {"message": "No hits found."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Vector Search utilizes a request of type SearchRequest.
# Encodes a query as a proper elastic search and returns the search result from the client.
@app.post("/search/vector")
async def vector_search(request: SearchRequest):
    try:
        # Formats as elastic search body and encodes the search request text to a vector.
        query = form_query(request.text, request.top_k)
        response = es.search(index=INDEX_NAME, body=query)
        results = []
        # Loops over the returned hits.
        for hit in response["hits"]["hits"]:
            # Access inner hits for embedded paper data.
            embedded_paper_hits = hit.get("inner_hits", {}).get("embedded_paper", {}).get("hits", {}).get("hits", [])
            # For each embedded hit...
            for embedded_hit in embedded_paper_hits:
                title_and_sentence = embedded_hit.get("fields", {}).get("embedded_paper", [{}])[0].get("title-and-sentence", [])
                # If there is data for the title-and-sentence...
                if title_and_sentence:
                    # Append relevant data to result.
                    results.append({
                        "doi": hit["_source"].get("metadata", {}).get("DOI", None),
                        "sentence": title_and_sentence[0],
                        "score": hit["_score"]
                    })

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

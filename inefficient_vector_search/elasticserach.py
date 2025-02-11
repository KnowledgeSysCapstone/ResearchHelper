import tensorflow_hub as hub
from elasticsearch import Elasticsearch

# Load the Universal Sentence Encoder model
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# Connect to Elasticsearch
es = Elasticsearch(hosts=["http://localhost:9200"])

# Input sentence
sentence = "I love hot dog"
query_vector = embed([sentence]).numpy().tolist()[0]

# Perform search
response = es.search(index="vector_index", body={
    "query": {
        "script_score": {
            "query": {
                "match_all": {}
            },
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                "params": {
                    "query_vector": query_vector
                }
            }
        }
    }
})

# Output results
print("Sentences most similar to the input sentence:")
for hit in response['hits']['hits']:
    print(f"Similarity: {hit['_score']}, Sentence: {hit['_source']['sentence']}") 
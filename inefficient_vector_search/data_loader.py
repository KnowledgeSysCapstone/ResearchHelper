import numpy as np
from elasticsearch import Elasticsearch

# 加载数据
embeddings = np.load("/Users/qiao/ResearchHelper/inefficient_vector_search/Hot_dog_encodings.npy")
with open("/Users/qiao/ResearchHelper/inefficient_vector_search/Hot_dog_sentences.txt", 'r') as f:
    sentences = f.readlines()

# 连接到 Elasticsearch
es = Elasticsearch(hosts=["http://localhost:9200"])

# 导入数据
for i, (vector, sentence) in enumerate(zip(embeddings, sentences)):
    es.index(index="vector_index", id=i, body={
        "sentence": sentence.strip(),
        "vector": vector.tolist()
    })
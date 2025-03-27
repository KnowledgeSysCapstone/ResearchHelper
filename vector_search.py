import json
import numpy as np
from elasticsearch import Elasticsearch
import argparse

# 获取环境变量
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('ELASTIC_PASSWORD='):
            elastic_password = line.strip().split('=')[1]
            break

# 配置 Elasticsearch 连接
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", elastic_password)
)

def search_by_doi(doi):
    """根据DOI搜索文档"""
    query = {
        "query": {
            "term": {
                "doi": doi
            }
        }
    }
    
    response = es.search(index="research_papers", body=query, size=10)
    print(f"找到 {response['hits']['total']['value']} 个匹配文档")
    
    for hit in response['hits']['hits']:
        print(f"DOI: {hit['_source']['doi']}")
        print(f"句子: {hit['_source']['sentences']}")
        print("---")

def search_by_vector(vector, top_k=5):
    """根据向量搜索最相似的文档"""
    query = {
        "knn": {
            "field": "sentence_vectors",
            "query_vector": vector,
            "k": top_k,
            "num_candidates": 100
        },
        "_source": ["doi", "sentences"]
    }
    
    response = es.search(index="research_papers", body=query)
    print(f"找到 {len(response['hits']['hits'])} 个相似文档")
    
    for i, hit in enumerate(response['hits']['hits']):
        print(f"#{i+1} 相似度得分: {hit['_score']}")
        print(f"DOI: {hit['_source']['doi']}")
        print(f"句子: {hit['_source']['sentences']}")
        print("---")

def get_random_vector():
    """从索引中随机获取一个向量用于演示"""
    query = {
        "query": {
            "function_score": {
                "random_score": {}
            }
        },
        "size": 1
    }
    
    response = es.search(index="research_papers", body=query)
    if response['hits']['hits']:
        vector = response['hits']['hits'][0]['_source']['sentence_vectors']
        doi = response['hits']['hits'][0]['_source']['doi']
        sentence = response['hits']['hits'][0]['_source']['sentences']
        return vector, doi, sentence
    return None, None, None

def main():
    parser = argparse.ArgumentParser(description='Elasticsearch向量搜索工具')
    parser.add_argument('--doi', help='根据DOI搜索文档')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    
    args = parser.parse_args()
    
    if args.doi:
        search_by_doi(args.doi)
    elif args.demo:
        print("=== 向量搜索演示 ===")
        vector, doi, sentence = get_random_vector()
        if vector:
            print("随机选择的文档:")
            print(f"DOI: {doi}")
            print(f"句子: {sentence}")
            print("\n搜索相似文档:")
            search_by_vector(vector)
        else:
            print("无法获取随机向量")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 
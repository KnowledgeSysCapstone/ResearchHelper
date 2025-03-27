import json
import requests
import os
import numpy as np
from elasticsearch import Elasticsearch
from tqdm import tqdm

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

# 检查Elasticsearch是否正在运行
try:
    es.info()
    print("已成功连接到 Elasticsearch")
except Exception as e:
    print(f"无法连接到 Elasticsearch: {e}")
    exit(1)

# 如果索引不存在，创建索引
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
    print("已创建 'research_papers' 索引")

# 加载原始文本数据
print("加载原始文本数据...")
with open('abstracts_parsed.txt', 'r') as f:
    data = f.read().strip()
    # 移除末尾可能存在的多余百分号
    if data.endswith('%'):
        data = data[:-1]
    parsed_data = json.loads(data)

# 加载向量化数据
print("加载向量化数据...")
try:
    with open('abstracts_vectorized.txt', 'r') as f:
        data = f.read().strip()
        if data.endswith('%'):
            data = data[:-1]
        vectorized_data = json.loads(data)
        print(f"成功加载向量化数据")
except json.JSONDecodeError as e:
    print(f"JSON解析错误: {e}")
    print("尝试使用逐行解析方法...")
    
    # 如果JSON解析失败，尝试手动解析
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
                
            # 计算括号的数量来追踪JSON结构
            bracket_count += line.count('{') - line.count('}')
            bracket_count += line.count('[') - line.count(']')
            
            combined_lines += line
            
            # 当括号平衡时，尝试解析完整的JSON对象
            if bracket_count == 0 and combined_lines.strip():
                try:
                    obj = json.loads(combined_lines)
                    vectorized_data = obj
                    combined_lines = ""
                    print("成功解析完整的JSON对象")
                    break
                except json.JSONDecodeError:
                    # 可能不是完整的JSON，继续添加行
                    pass

print(f"解析了 {len(parsed_data)} 个DOI的原始文本")
print(f"解析了 {len(vectorized_data)} 个DOI的向量数据")

# 上传数据到 Elasticsearch
print("上传数据到 Elasticsearch...")
bulk_data = []
count = 0

for doi, sentences in tqdm(parsed_data.items()):
    if doi in vectorized_data:
        vectors = vectorized_data[doi]
        # 确保句子和向量数量一致
        min_len = min(len(sentences), len(vectors))
        
        for i in range(min_len):
            # 准备文档
            doc = {
                "doi": doi,
                "sentences": sentences[i],
                "sentence_vectors": vectors[i]
            }
            
            # 准备批量操作
            bulk_data.append({"index": {"_index": "research_papers"}})
            bulk_data.append(doc)
            count += 1
            
            # 每2000个文档批量提交一次
            if len(bulk_data) >= 4000:
                print(f"批量上传 {len(bulk_data)//2} 个文档...")
                try:
                    es.bulk(body=bulk_data)
                    print(f"已上传 {count} 个文档")
                except Exception as e:
                    print(f"上传时出错: {e}")
                bulk_data = []

# 提交剩余数据
if bulk_data:
    print(f"上传剩余的 {len(bulk_data)//2} 个文档...")
    try:
        es.bulk(body=bulk_data)
        print(f"已上传总计 {count} 个文档")
    except Exception as e:
        print(f"上传剩余数据时出错: {e}")

print("完成！数据已成功上传到 Elasticsearch。") 
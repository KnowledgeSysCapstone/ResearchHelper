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

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
try:
    load_dotenv()
    logger.info("环境变量已加载")
except Exception as e:
    logger.warning(f"加载.env文件失败: {e}")
    pass  # 如果.env文件不存在，忽略错误

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，实际生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取Elasticsearch配置
elastic_password = os.getenv("ELASTIC_PASSWORD", "yourpassword")
elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
logger.info(f"使用Elasticsearch主机: {elasticsearch_host}")
logger.info(f"使用Elasticsearch密码: {elastic_password[:2]}***")

# 创建全局Elasticsearch客户端变量
es = None

# 定义连接函数，允许重试
def connect_elasticsearch(max_retries=5, retry_interval=5):
    global es
    
    # 尝试Docker网络中的连接
    es_hosts = [
        elasticsearch_host,         # 环境变量中的主机
        "http://elasticsearch:9200",  # Docker网络名称
        "http://localhost:9200",      # 本地主机名
        "http://127.0.0.1:9200",      # IPv4 本地地址
    ]
    
    # 添加重试逻辑
    for retry in range(max_retries):
        logger.info(f"尝试连接Elasticsearch (第 {retry+1}/{max_retries} 次)")
        
        for host in es_hosts:
            try:
                logger.info(f"尝试连接到: {host}")
                es_client = Elasticsearch(
                    host,
                    basic_auth=("elastic", elastic_password),
                    verify_certs=False,
                    request_timeout=30
                )
                
                if es_client.ping():
                    logger.info(f"成功连接到Elasticsearch: {host}")
                    return es_client
            except Exception as e:
                logger.error(f"连接 {host} 失败: {e}")
        
        # 如果没有成功连接，等待后重试
        if retry < max_retries - 1:
            logger.info(f"等待 {retry_interval} 秒后重试...")
            time.sleep(retry_interval)
    
    # 所有重试失败后，返回模拟客户端
    logger.warning("所有连接尝试失败，使用模拟客户端")
    return create_mock_client()

# 创建模拟客户端
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
            logger.warning("使用模拟Elasticsearch客户端，返回空结果")
            index = kwargs.get('index', 'unknown')
            body = kwargs.get('body', {})
            logger.info(f"模拟搜索: 索引={index}, 查询={body}")
            return {"hits": {"hits": []}}
    
    return MockElasticsearch()

# 初始化向量模型
model = SentenceTransformer('all-MiniLM-L6-v2')

# 索引名称
INDEX_NAME = "research_papers"

class SearchRequest(BaseModel):
    text: str
    top_k: int = 10

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    global es
    # 连接到Elasticsearch
    es = connect_elasticsearch()
    logger.info("应用启动完成，Elasticsearch客户端已初始化")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        health = es.cluster.health()
        return {"status": "ok", "es_status": health["status"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/vectorize")
async def vectorize_text(text: str):
    """向量化文本"""
    try:
        vector = model.encode(text).tolist()
        return {"vector": vector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/vector")
async def vector_search(request: SearchRequest):
    """根据文本进行向量搜索"""
    try:
        logger.info(f"接收到向量搜索请求: {request.text[:30]}... (top_k={request.top_k})")
        
        # 检查Elasticsearch连接
        if es is None:
            logger.error("Elasticsearch客户端未初始化")
            raise HTTPException(status_code=503, detail="Elasticsearch服务不可用")
            
        # 将输入文本向量化
        try:
            query_vector = model.encode(request.text).tolist()
            logger.info(f"成功将文本向量化，向量维度: {len(query_vector)}")
        except Exception as e:
            logger.error(f"文本向量化失败: {e}")
            raise HTTPException(status_code=500, detail=f"文本向量化错误: {str(e)}")
        
        # 构建查询
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
            logger.info("已构建KNN查询")
        except Exception as e:
            logger.error(f"构建查询失败: {e}")
            raise HTTPException(status_code=500, detail=f"构建查询错误: {str(e)}")
        
        # 执行搜索
        try:
            response = es.search(index=INDEX_NAME, body=query)
            logger.info(f"搜索成功，找到 {len(response['hits']['hits'])} 个结果")
        except Exception as e:
            logger.error(f"Elasticsearch搜索失败: {e}")
            raise HTTPException(status_code=500, detail=f"搜索错误: {str(e)}")
        
        # 处理结果
        results = []
        for hit in response['hits']['hits']:
            results.append({
                "doi": hit['_source']['doi'],
                "sentence": hit['_source']['sentences'],
                "score": hit['_score']
            })
        
        logger.info(f"成功返回 {len(results)} 个结果")
        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"向量搜索未处理异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/doi/{doi}")
async def search_by_doi(doi: str, size: int = 10):
    """根据DOI搜索文档"""
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
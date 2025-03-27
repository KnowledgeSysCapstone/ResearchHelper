# Research Helper - 向量搜索系统

这是一个基于Elasticsearch的向量搜索系统，可以通过向量相似度搜索研究论文中的句子。

## 项目架构

- **Elasticsearch**: 提供向量存储和搜索功能
- **FastAPI后端**: 提供向量化和搜索API
- **Next.js前端**: 提供用户界面

## 启动服务

使用Docker Compose启动所有服务：

```bash
docker-compose up --build
```

启动后，可以访问以下服务：

- Elasticsearch: http://localhost:9200
- FastAPI后端: http://localhost:8000
- Next.js前端: http://localhost:3000

## 数据加载

系统使用了两个关键文件：

- `abstracts_parsed.txt`: 包含原始句子数据，以DOI为索引
- `abstracts_vectorized.txt`: 包含句子的向量表示

要将数据加载到Elasticsearch，请运行：

```bash
python upload_data.py
```

## 功能使用

1. 访问前端界面: http://localhost:3000
2. 在搜索框中输入您想要搜索的文本
3. 系统会将文本转换为向量并搜索最相似的句子
4. 查看搜索结果，包含DOI、相似度分数和句子内容

## API接口

后端提供以下API接口：

- **向量搜索**: `POST /search/vector` - 通过文本搜索相似句子
- **DOI搜索**: `GET /search/doi/{doi}` - 根据DOI查找句子
- **健康检查**: `GET /health` - 检查系统状态

## 向量搜索演示

使用命令行工具进行向量搜索演示：

```bash
python vector_search.py --demo
```
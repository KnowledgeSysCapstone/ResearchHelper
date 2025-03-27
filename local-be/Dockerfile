FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 预下载sentence-transformers模型
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 设置环境变量
ENV ELASTIC_PASSWORD=yourpassword
ENV ELASTICSEARCH_HOST=http://elasticsearch:9200

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
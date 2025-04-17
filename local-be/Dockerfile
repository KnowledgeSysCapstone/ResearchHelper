# Build the Environment using Slim / Stable Python
# FastAPI rec. 3.10+, Sentence Transformers 3.9+, Elasticsearch 3.8+
FROM python:3.11-slim

# Using /app for working directory for service.
WORKDIR /app

# Copy the requirements text file.
COPY requirements.txt .
# Install each dependency.
RUN pip install --no-cache-dir -r requirements.txt

# Pre-Download and Cache Sentence Transformer Model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

# Start Uvicorn ASGI server @ :8000
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
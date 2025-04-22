# Research Helper - Vector Search System

A vector search system based on Elasticsearch for finding research papers relevent to a claim.

Simple use steps:
1. Clone repo.
2. ```docker-compose up --build```
3. Wait until build finishes.
4. Install dependencies for uploading (see Prereqs.).
5. ```python uploader.py``` | 
This will take a large amount of time (depending on settings). Go play some games or something.
Default topic is papers concerning "food".
6. Access front end at http://localhost:3000.
7. Type a food-related claim and press search.

## System Architecture

- **Elasticsearch**: Provides vector storage and search functionality.
- **FastAPI Backend**: Provides vectorization and search APIs.
- **Next.js Frontend**: Provides user interface.

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Node.js 18+

If utilizing the uploader to populate the database, you will need the following pip packages:
- requests
- beautifulsoup4
- sentence-transformers
- spacy
- lxml
- elasticsearch
- tqdm

You may be able to utilize the command:
```bash
pip install requests beautifulsoup4 sentence-transformers spacy lxml elasticsearch tqdm
```
to install these requirements at once.

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/KnowledgeSysCapstone/ResearchHelper.git
cd ResearchHelper
```

2. Create `.env` file (or modify that provided) with the following content:
```bash
STACK_VERSION=9.0.0
ES_PORT=9200
ELASTICSEARCH_HOST=http://elasticsearch:9200
ELASTIC_PASSWORD=testpass
```

## Starting the Services

Start all services using Docker Compose:

```bash
docker-compose up --build
```

After startup processes, you can access the following services:

- Elasticsearch: http://localhost:9200
- FastAPI backend: http://localhost:8000
- Next.js frontend: http://localhost:3000

Please be patient for the project to build.

### Creating Elasticsearch Index and Uploading Data

Data upload should occur after the initial clone and docker-compose up.
The upload system will automatically create the required index when uploading data.
This system requires two key files:

- `collect_documents.py`: Dependency for uploading that collects documents using a chosen subject.
- `uploader.py`: Contains the uploading logic.

Uploader utilizes:
```def get_documents(keyword: str, min_abstracts: int = 5000, min_cited: int = 100, do_print: bool = False) -> Iterator[dict[str]]:```

To change the default document retrieval of uploading, go to line 41 in uploader.py and modify:
- str = desired topic
- min_abstracts and min_cited filters as needed (these ignore providers of lower quality papers)

The default behavior produces a DB with files related to the topic "food".

To upload data to Elasticsearch, run:
```bash
python uploader.py
```

The script will:
1. Connect to Elasticsearch
2. Create the index if it doesn't exist
3. Collect data using collect_documents.py
4. Upload documents in batches
5. Report progress and completion

## Using the System

1. Visit the frontend interface: http://localhost:3000
2. Enter your search text in the search box
3. The system will convert the text to a vector and find the most similar sentences
4. View the search results, including DOI, similarity score, and sentence content

## API Endpoints

The backend provides the following API endpoints:

- **Vector Search**: `POST /search/vector` - Search for similar sentences by text
- **DOI Search**: `GET /search/doi/{doi}` - Find sentences by DOI

## Troubleshooting

- **Elasticsearch Connection Issues**: Check if Elasticsearch is running with `curl -u elastic:testpassword http://localhost:9200`
- **Backend Issues**: Check logs with `docker logs fastapi_backend`
- **Frontend Issues**: Check logs with `docker logs nextjs_frontend`
- **Data Issues**: Delete elasticsearch data from docker and re-run `uploader.py`

## Clearing and Rebuilding the Index Manually

To clear the index and reupload data:

```bash
# Delete the index.
curl -XDELETE -u elastic:testpassword "http://localhost:9200/research_papers"

# Reupload data.
python upload_data.py
```
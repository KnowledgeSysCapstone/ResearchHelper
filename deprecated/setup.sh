#!/bin/bash
# Run to setup the entire back end on fresh linux VM.

set -e

# 1. Install python.
echo "Python installation..."
sudo apt update
sudo apt install python3 python3-pip -y
sudo apt install python3-elasticsearch python3-fastapi python3-uvicorn -y

# 2. Install and start Elasticsearch
echo "Installing Elasticsearch..."
curl -fsSL https://elastic.co/start-local | sh
cd elastic-start-local || exit

echo "Elasticsearch installed. Stopping then starting Elasticsearch..."
sudo ./stop.sh
sleep 20
sudo ./start.sh &

echo "Waiting for Elasticsearch to initialize..."
sleep 60

# 3. Store the Elasticsearch API key (if not already in .env).
if [ ! -f ".env" ]; then
    sudo touch .env
fi

# Check if the API key is already set in the environment, if not, log an error.
if ! grep -q "ES_LOCAL_API_KEY" .env; then
    echo "ES_LOCAL_API_KEY not found in .env. Please set it manually or ensure it's generated during setup."
    exit 1
fi

echo "Elasticsearch API Key found in .env."

cd ..

# 4. Populate Elasticsearch with data from a given Python script
if [ -n "$1" ]; then
    echo "Running population script: $1"
    # Export environment variables for the population script
    export $(grep -v '^#' .env | xargs)  # Load .env variables

    python3 "$1"  # Populate Elasticsearch with data
    echo "Elasticsearch populated."
else
    echo "No population script provided. Skipping population step."
fi

# 5. Start FastAPI server
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &  # Start FastAPI in the background

echo "All services should be running."
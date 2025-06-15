#!/bin/bash

# Run the RAG chatbot demo
# This script runs the demo for the RAG chatbot

echo "Starting RAG chatbot demo..."

# Change to the project directory
cd "$(dirname "$0")"

# Check if Qdrant is running
if ! nc -z localhost 6333 &>/dev/null; then
    echo "Starting Qdrant using Docker..."
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
    
    # Wait for Qdrant to start
    echo "Waiting for Qdrant to start..."
    sleep 5
fi

# Run the demo
python demo.py

# Check the exit code
if [ $? -ne 0 ]; then
    echo "Demo exited with an error."
    exit 1
fi

echo "Demo completed."

#!/bin/bash

# Run tests for the RAG chatbot
# This script runs the unit tests for the RAG chatbot

echo "Running tests for RAG chatbot..."

# Change to the project directory
cd "$(dirname "$0")"

# Run the tests
python -m unittest discover -s tests

# Check the exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Some tests failed."
fi

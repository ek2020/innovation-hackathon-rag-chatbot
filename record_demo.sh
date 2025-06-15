#!/bin/bash

# Record a demo of the RAG chatbot
# This script records a demo of the RAG chatbot using asciinema

echo "Recording RAG chatbot demo..."

# Check if asciinema is installed
if ! command -v asciinema &> /dev/null; then
    echo "asciinema is not installed. Please install it first:"
    echo "  pip install asciinema"
    exit 1
fi

# Change to the project directory
cd "$(dirname "$0")"

# Create recordings directory if it doesn't exist
mkdir -p recordings

# Start recording
echo "Starting recording... Press Ctrl+D to stop recording when done."
echo "The recording will be saved to recordings/rag_chatbot_demo.cast"
echo ""
echo "3..."
sleep 1
echo "2..."
sleep 1
echo "1..."
sleep 1

# Record the demo
asciinema rec recordings/rag_chatbot_demo.cast -c "./run_demo.sh"

echo ""
echo "Recording saved to recordings/rag_chatbot_demo.cast"
echo ""
echo "To play the recording, run:"
echo "  asciinema play recordings/rag_chatbot_demo.cast"
echo ""
echo "To upload the recording to asciinema.org, run:"
echo "  asciinema upload recordings/rag_chatbot_demo.cast"
echo ""
echo "To convert the recording to a GIF, you can use tools like:"
echo "  asciicast2gif (https://github.com/asciinema/asciicast2gif)"
echo ""

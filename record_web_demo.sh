#!/bin/bash

# Record a video of the RAG chatbot web interface
# This script records a video of the RAG chatbot web interface using FFmpeg

echo "Recording RAG chatbot web interface demo..."

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg is not installed. Please install it first."
    echo "For macOS: brew install ffmpeg"
    echo "For Ubuntu: sudo apt-get install ffmpeg"
    echo "For Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

# Change to the project directory
cd "$(dirname "$0")"

# Create recordings directory if it doesn't exist
mkdir -p recordings

# Set recording parameters
DURATION=300  # Recording duration in seconds (5 minutes)
OUTPUT_FILE="recordings/rag_chatbot_web_demo.mp4"
RESOLUTION="1280x720"  # 720p resolution
FRAMERATE=15  # 15 frames per second

# Start the application in the background
echo "Starting the application..."
echo "Please wait for the application to start..."

# Start the API server
echo "Starting API server..."
(cd "$(dirname "$0")" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000) &
API_PID=$!

# Wait for the API server to start
sleep 5

# Start the frontend
echo "Starting frontend..."
(cd "$(dirname "$0")" && streamlit run frontend/app.py) &
FRONTEND_PID=$!

# Wait for the frontend to start
sleep 5

# Open the browser
echo "Opening browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:8501
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:8501
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start http://localhost:8501
else
    echo "Please open http://localhost:8501 in your browser"
fi

# Wait for the user to be ready
echo ""
echo "The application is now running."
echo "Please arrange your browser window for recording."
echo "The recording will start in 10 seconds and will last for $DURATION seconds."
echo "Press Ctrl+C to cancel."
echo ""

for i in {10..1}; do
    echo "$i..."
    sleep 1
done

# Start recording
echo "Recording started. Please interact with the application."
echo "Recording will stop automatically after $DURATION seconds."
echo "Press Ctrl+C to stop recording early."

# Determine the screen recording command based on the OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    ffmpeg -f avfoundation -framerate $FRAMERATE -i "1" -t $DURATION -s $RESOLUTION -c:v libx264 -pix_fmt yuv420p $OUTPUT_FILE
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    ffmpeg -f x11grab -framerate $FRAMERATE -i :0.0 -t $DURATION -s $RESOLUTION -c:v libx264 -pix_fmt yuv420p $OUTPUT_FILE
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    ffmpeg -f gdigrab -framerate $FRAMERATE -i desktop -t $DURATION -s $RESOLUTION -c:v libx264 -pix_fmt yuv420p $OUTPUT_FILE
else
    echo "Unsupported OS for screen recording."
    echo "Please use a screen recording tool appropriate for your OS."
fi

# Stop the application
echo "Stopping the application..."
kill $FRONTEND_PID
kill $API_PID

echo ""
echo "Recording saved to $OUTPUT_FILE"
echo ""

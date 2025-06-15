#!/usr/bin/env python3
"""
Script to run the RAG chatbot locally for testing.
"""

import os
import argparse
import subprocess
import time
import webbrowser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_api():
    """Run the FastAPI server."""
    print("Starting API server...")
    subprocess.Popen(["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    print("API server running at http://localhost:8000")
    print("API documentation available at http://localhost:8000/docs")

def run_frontend():
    """Run the Streamlit frontend."""
    print("Starting frontend...")
    subprocess.Popen(["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"])
    print("Frontend running at http://localhost:8501")

def run_qdrant():
    """Run Qdrant using Docker."""
    print("Starting Qdrant...")
    # Check if Docker is installed
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Docker not found. Please install Docker to run Qdrant.")
        return False
    
    # Check if Qdrant container is already running
    result = subprocess.run(
        ["docker", "ps", "-q", "-f", "name=qdrant"],
        check=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    if result.stdout:
        print("Qdrant is already running.")
        return True
    
    # Run Qdrant container
    try:
        subprocess.run([
            "docker", "run", "-d",
            "--name", "qdrant",
            "-p", "6333:6333",
            "-p", "6334:6334",
            "-v", "qdrant_data:/qdrant/storage",
            "qdrant/qdrant:latest"
        ], check=True)
        print("Qdrant running at http://localhost:6333")
        return True
    except subprocess.SubprocessError:
        print("Failed to start Qdrant container.")
        return False

def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description="Run the RAG chatbot locally.")
    parser.add_argument("--no-qdrant", action="store_true", help="Don't start Qdrant")
    parser.add_argument("--no-api", action="store_true", help="Don't start API server")
    parser.add_argument("--no-frontend", action="store_true", help="Don't start frontend")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    
    args = parser.parse_args()
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Start Qdrant
    if not args.no_qdrant:
        qdrant_success = run_qdrant()
        if not qdrant_success:
            print("Warning: Qdrant failed to start. The application may not work correctly.")
    
    # Start API server
    if not args.no_api:
        run_api()
    
    # Start frontend
    if not args.no_frontend:
        run_frontend()
    
    # Wait for services to start
    print("Waiting for services to start...")
    time.sleep(5)
    
    # Open browser
    if not args.no_browser and not args.no_frontend:
        webbrowser.open("http://localhost:8501")
    
    print("\nPress Ctrl+C to stop all services.")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        
        # Stop Qdrant container if we started it
        if not args.no_qdrant:
            try:
                subprocess.run(["docker", "stop", "qdrant"], check=False)
                subprocess.run(["docker", "rm", "qdrant"], check=False)
            except:
                pass
        
        print("Services stopped.")

if __name__ == "__main__":
    main()

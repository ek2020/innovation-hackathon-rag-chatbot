#!/bin/bash

# Initialize Git repository and make first commit
# This script sets up a Git repository for the RAG chatbot project

echo "Initializing Git repository for RAG chatbot..."

# Initialize Git repository
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: RAG chatbot with Azure OpenAI"

# Instructions for adding a remote repository
echo ""
echo "Git repository initialized successfully!"
echo ""
echo "To add a remote repository, use the following commands:"
echo "  git remote add origin <your-repository-url>"
echo "  git branch -M main"
echo "  git push -u origin main"
echo ""
echo "Done!"

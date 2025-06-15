#!/usr/bin/env python3
"""
Demo script for the RAG chatbot.
This script demonstrates how to use the RAG chatbot with sample documents.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from app.services.rag_service import rag_service
from app.services.conversation import conversation_service

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the demo header."""
    print("=" * 80)
    print("RAG Chatbot Demo".center(80))
    print("=" * 80)
    print("This demo shows how to use the RAG chatbot with sample documents.")
    print("=" * 80)
    print()

def process_sample_documents():
    """Process the sample documents."""
    print("Processing sample documents...")
    
    # Get sample documents
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_documents")
    company_profile = os.path.join(sample_dir, "company_profile.txt")
    developer_profile = os.path.join(sample_dir, "developer_profile.txt")
    project_sow = os.path.join(sample_dir, "project_sow.txt")
    
    # Process documents
    print(f"Processing {os.path.basename(company_profile)}...")
    rag_service.process_and_store_document(company_profile)
    
    print(f"Processing {os.path.basename(developer_profile)}...")
    rag_service.process_and_store_document(developer_profile)
    
    print(f"Processing {os.path.basename(project_sow)}...")
    rag_service.process_and_store_document(project_sow)
    
    print("All documents processed successfully!")
    print()

def chat_demo():
    """Run the chat demo."""
    print("Starting chat demo...")
    print("Type 'exit' to quit the demo.")
    print()
    
    # Create a new session
    session_id = conversation_service.create_session()
    print(f"Session ID: {session_id}")
    print()
    
    # Chat loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Exiting chat demo...")
            break
        
        # Process user input
        print("Bot: ", end="", flush=True)
        
        # Query the RAG system
        result = rag_service.query(user_input, session_id)
        
        # Print the response
        print(result["response"])
        
        # Print sources
        if result["sources"]:
            print("\nSources:")
            for source in result["sources"]:
                print(f"- {source['source']} (Score: {source['score']:.2f})")
        
        print()

def profile_matching_demo():
    """Run the profile matching demo."""
    print("Starting profile matching demo...")
    print()
    
    # Get sample documents
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_documents")
    developer_profile = os.path.join(sample_dir, "developer_profile.txt")
    project_sow = os.path.join(sample_dir, "project_sow.txt")
    
    # Match profiles to SOW
    print("Matching developer profile to project SOW...")
    matches = rag_service.match_profiles_to_sow(
        profile_file_paths=[developer_profile],
        sow_file_path=project_sow
    )
    
    # Print results
    print("\nMatch Results:")
    for match in matches:
        match_score = match["match_score"] * 100
        print(f"{match['name']}: {match_score:.1f}% match")
        print(f"Matching skills: {', '.join(match['matching_skills'])}")
        print(f"All skills: {', '.join(match['all_skills'])}")
    
    print()

def main():
    """Main function."""
    clear_screen()
    print_header()
    
    # Process sample documents
    process_sample_documents()
    
    # Menu loop
    while True:
        print("Demo Menu:")
        print("1. Chat with documents")
        print("2. Profile matching")
        print("3. Exit")
        print()
        
        # Get user choice
        choice = input("Enter your choice (1-3): ")
        print()
        
        if choice == "1":
            chat_demo()
        elif choice == "2":
            profile_matching_demo()
        elif choice == "3":
            print("Exiting demo...")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print()

if __name__ == "__main__":
    main()

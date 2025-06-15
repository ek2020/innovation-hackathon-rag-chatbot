import streamlit as st
import requests
import os
import json
from typing import List, Dict, Any
import time

# API settings
API_URL = os.environ.get("API_URL", "http://api:8000/api")

# Page configuration
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if "session_id" not in st.session_state:
    # Create a new session
    response = requests.post(f"{API_URL}/sessions")
    st.session_state.session_id = response.json()["session_id"]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

# Functions
def load_documents():
    """Load documents from the API."""
    try:
        response = requests.get(f"{API_URL}/documents")
        if response.status_code == 200:
            st.session_state.documents = response.json()["documents"]
        else:
            st.error(f"Error loading documents: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")

def upload_document(file):
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file, "application/octet-stream")}
        response = requests.post(f"{API_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                st.success(result["message"])
                load_documents()  # Refresh document list
            else:
                st.error(result["message"])
        else:
            st.error(f"Error uploading document: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")

def delete_document(document_id):
    """Delete a document from the API."""
    try:
        response = requests.delete(f"{API_URL}/documents/{document_id}")
        
        if response.status_code == 200:
            st.success(f"Document deleted successfully")
            load_documents()  # Refresh document list
        else:
            st.error(f"Error deleting document: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")

def query_rag(query: str):
    """Query the RAG system."""
    try:
        payload = {
            "query": query,
            "session_id": st.session_state.session_id,
            "top_k": 3
        }
        
        response = requests.post(f"{API_URL}/query", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error querying RAG system: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def match_profiles(profile_ids: List[str], sow_id: str):
    """Match profiles to a Statement of Work."""
    try:
        payload = {
            "profile_ids": profile_ids,
            "sow_id": sow_id
        }
        
        response = requests.post(f"{API_URL}/match", json=payload)
        
        if response.status_code == 200:
            return response.json()["matches"]
        else:
            st.error(f"Error matching profiles: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def clear_chat():
    """Clear the chat history."""
    st.session_state.messages = []

def new_session():
    """Create a new session."""
    try:
        response = requests.post(f"{API_URL}/sessions")
        st.session_state.session_id = response.json()["session_id"]
        st.session_state.messages = []
        st.success("New session created")
    except Exception as e:
        st.error(f"Error creating new session: {str(e)}")

# Sidebar
with st.sidebar:
    st.title("RAG Chatbot")
    st.markdown("---")
    
    # Document management
    st.subheader("Document Management")
    
    # Upload document
    uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        if st.button("Process Document"):
            upload_document(uploaded_file)
    
    # Document list
    st.subheader("Documents")
    if st.button("Refresh Documents"):
        load_documents()
    
    # Display documents
    if st.session_state.documents:
        for doc in st.session_state.documents:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{doc['name']} ({doc['type']})")
            with col2:
                if st.button("Delete", key=f"delete_{doc['id']}"):
                    delete_document(doc['id'])
    else:
        st.info("No documents uploaded yet")
    
    # Profile matching
    st.markdown("---")
    st.subheader("Profile Matching")
    
    # Select profiles and SOW
    if st.session_state.documents:
        profile_options = [doc["id"] for doc in st.session_state.documents]
        selected_profiles = st.multiselect("Select Profiles", profile_options)
        selected_sow = st.selectbox("Select Statement of Work", [""] + profile_options)
        
        if selected_profiles and selected_sow and st.button("Match Profiles"):
            matches = match_profiles(selected_profiles, selected_sow)
            
            if matches:
                st.subheader("Match Results")
                for match in matches:
                    match_score = match["match_score"] * 100
                    st.write(f"{match['name']}: {match_score:.1f}% match")
                    st.write(f"Matching skills: {', '.join(match['matching_skills'])}")
                    st.markdown("---")
            else:
                st.info("No matches found")
    else:
        st.info("Upload documents to use profile matching")
    
    # Session management
    st.markdown("---")
    st.subheader("Session Management")
    st.write(f"Session ID: {st.session_state.session_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Session"):
            new_session()
    with col2:
        if st.button("Clear Chat"):
            clear_chat()

# Main chat interface
st.title("Chat with Documents")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Show sources if available
        if "sources" in message and message["sources"]:
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(f"- {source['source']} (Score: {source['score']:.2f})")

# Chat input
if prompt := st.chat_input("Ask a question about your documents"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get response from RAG system
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_rag(prompt)
            
            if response:
                st.write(response["response"])
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"],
                    "sources": response["sources"]
                })
                
                # Show sources
                if response["sources"]:
                    with st.expander("Sources"):
                        for source in response["sources"]:
                            st.write(f"- {source['source']} (Score: {source['score']:.2f})")
            else:
                st.error("Failed to get response from the RAG system")

# Load documents on startup
if not st.session_state.documents:
    load_documents()

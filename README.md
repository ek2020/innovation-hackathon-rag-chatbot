# RAG Chatbot with Azure OpenAI

A Retrieval Augmented Generation (RAG) chatbot built from scratch using Azure OpenAI, without relying on frameworks like LangChain or LlamaIndex.

## Features

- Document processing for PDF, DOCX, and TXT files
- Semantic search using Qdrant vector database
- Conversation history and follow-up questions
- Profile matching based on skills
- Simple web interface built with Streamlit
- API built with FastAPI

## Architecture

The application follows a modular architecture with the following components:

1. **Document Processing**: Handles reading and chunking documents
2. **Vector Database**: Stores document embeddings for semantic search
3. **Azure OpenAI Integration**: Generates embeddings and responses
4. **Conversation Management**: Handles session and message history
5. **API Layer**: Exposes functionality through REST endpoints
6. **Frontend**: Provides a user interface for interacting with the system

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional, for containerized deployment)
- Azure OpenAI API access

## Installation

### Option 1: Local Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rag-chatbot.git
   cd rag-chatbot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` and update the values
   - Or set the environment variables directly

4. Run the API:
   ```
   uvicorn app.main:app --reload
   ```

5. Run the frontend:
   ```
   streamlit run frontend/app.py
   ```

### Option 2: Docker Deployment

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rag-chatbot.git
   cd rag-chatbot
   ```

2. Update the `.env` file with your Azure OpenAI credentials

3. Build and run the containers:
   ```
   docker-compose up -d
   ```

4. Access the application:
   - API: http://localhost:8000
   - Frontend: http://localhost:8501

## Usage

### Document Upload

1. Navigate to the frontend at http://localhost:8501
2. Use the sidebar to upload documents (PDF, DOCX, TXT)
3. Click "Process Document" to index the document

### Chatting with Documents

1. Type your question in the chat input
2. The system will retrieve relevant information from your documents
3. View source documents by expanding the "Sources" section

### Profile Matching

1. Upload profile documents and a Statement of Work (SOW)
2. Select the profiles and SOW in the sidebar
3. Click "Match Profiles" to see matching results

## API Documentation

The API documentation is available at http://localhost:8000/docs when the server is running.

Key endpoints:

- `POST /api/sessions`: Create a new conversation session
- `POST /api/upload`: Upload and process a document
- `POST /api/query`: Query the RAG system
- `POST /api/match`: Match profiles to a Statement of Work
- `GET /api/documents`: List all uploaded documents

## Project Structure

```
rag-chatbot/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── azure_openai.py
│   │   ├── conversation.py
│   │   ├── document_processor.py
│   │   ├── rag_service.py
│   │   └── vector_store.py
│   ├── __init__.py
│   └── main.py
├── frontend/
│   └── app.py
├── uploads/
├── .env
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.frontend
├── README.md
└── requirements.txt
```

## Customization

### Changing Vector Database

The system is designed to work with Qdrant by default, but you can modify the `vector_store.py` file to use other vector databases like FAISS.

### Adjusting Chunking Strategy

You can modify the chunking parameters in the `.env` file:
- `CHUNK_SIZE`: Maximum size of each chunk in characters
- `CHUNK_OVERLAP`: Number of characters to overlap between chunks

## License

This project is licensed under the MIT License - see the LICENSE file for details.





![alt text](<Screenshot 2025-06-15 at 11.42.28 PM.png>)



![alt text](<Screenshot 2025-06-16 at 12.16.25 AM.png>) 
![alt text](<Screenshot 2025-06-16 at 12.16.12 AM.png>) 

![alt text](<Screenshot 2025-06-16 at 12.16.03 AM.png>)

![alt text](<Screenshot 2025-06-16 at 12.21.39 AM.png>)


/Users/karthick/Desktop/rag-chatbot/Screen Recording 2025-06-16 at 12.49.09 AM.mov
# RAG Workflow Project

This repository contains a comprehensive implementation of a Retrieval Augmented Generation (RAG) workflow using Azure OpenAI and Qdrant vector database.

## Project Overview

Retrieval Augmented Generation (RAG) is an AI architecture that enhances large language models by retrieving relevant information from a knowledge base before generating responses. This approach combines the reasoning capabilities of LLMs with the accuracy and specificity of your own data.

## Architecture

Our RAG implementation follows a modular architecture with the following components:

1. **Document Processing**: Handles reading and chunking documents from various formats (PDF, DOCX, TXT)
2. **Vector Database**: Stores document embeddings for semantic search using Qdrant
3. **Azure OpenAI Integration**: Generates embeddings and responses
4. **Conversation Management**: Handles session and message history
5. **API Layer**: Exposes functionality through REST endpoints using FastAPI
6. **Frontend**: Provides a user interface using Streamlit

For a detailed architecture diagram, see [rag_architecture.md](./rag_architecture.md).

## RAG Workflow

### Document Processing Flow

1. User uploads a document through the UI
2. Document is processed and split into chunks
3. Azure OpenAI generates embeddings for each chunk
4. Embeddings and metadata are stored in Qdrant

### Query Processing Flow

1. User submits a question
2. System retrieves conversation history (if any)
3. Question is contextualized if it's a follow-up
4. Question is converted to an embedding
5. Relevant document chunks are retrieved from Qdrant
6. Azure OpenAI generates a response based on the question and retrieved context
7. Response is returned to the user with source attribution

## Features

- **Multi-format Document Support**: Process PDF, DOCX, and TXT files
- **Semantic Search**: Find relevant information based on meaning, not just keywords
- **Conversation History**: Support for follow-up questions with context
- **Source Attribution**: Responses include references to source documents
- **Profile Matching**: Match profiles to requirements based on extracted skills
- **Containerized Deployment**: Easy deployment with Docker and Docker Compose

## Presentation

For a detailed presentation of the RAG workflow, see [rag_presentation.html](./rag_presentation.html).

## Implementation Details

### Backend (FastAPI)

- Modular service architecture
- RESTful API endpoints
- Background task processing
- Session management

### Vector Database (Qdrant)

- Efficient similarity search
- Metadata storage
- Scalable architecture

### Frontend (Streamlit)

- Interactive chat interface
- Document management
- Profile matching visualization

### Azure OpenAI Integration

- Embedding generation
- Chat completions
- Query contextualization

## Use Cases

- **Customer Support**: Answer customer queries based on product documentation
- **Legal Document Analysis**: Extract insights from contracts and regulations
- **Research Assistant**: Find relevant information across large collections of papers
- **Internal Knowledge Base**: Make company documentation easily accessible
- **Talent Matching**: Match candidate profiles to job requirements

## Future Enhancements

- Advanced document processing (tables, images, structured data)
- Multi-modal RAG (incorporating image and audio content)
- Hybrid search (combining semantic and keyword search)
- User feedback loop
- Advanced analytics
- Enterprise integration

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)
- Azure OpenAI API access

### Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and update with your Azure OpenAI credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run the API: `uvicorn app.main:app --reload`
5. Run the frontend: `streamlit run frontend/app.py`

### Docker Deployment

1. Update the `.env` file with your Azure OpenAI credentials
2. Build and run the containers: `docker-compose up -d`
3. Access the application:
   - API: http://localhost:8000
   - Frontend: http://localhost:8501

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Azure OpenAI for providing the embedding and completion models
- Qdrant for the vector database
- FastAPI and Streamlit for the backend and frontend frameworks

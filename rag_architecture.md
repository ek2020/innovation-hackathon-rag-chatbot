# RAG Chatbot Architecture

This document outlines the architecture of our Retrieval Augmented Generation (RAG) chatbot built using Azure OpenAI.

## Architecture Diagram

```mermaid
graph TD
    subgraph "Frontend Layer"
        UI[Streamlit UI]
    end

    subgraph "API Layer"
        API[FastAPI]
        Routes[API Routes]
    end

    subgraph "Core Services"
        RAG[RAG Service]
        Conv[Conversation Service]
        Doc[Document Processor]
        Vector[Vector Store]
        AzureAI[Azure OpenAI Service]
    end

    subgraph "Storage"
        Qdrant[(Qdrant Vector DB)]
        FileSystem[(File System)]
    end

    %% User interactions
    User((User)) -->|Uploads Documents| UI
    User -->|Asks Questions| UI
    
    %% Frontend to API
    UI -->|HTTP Requests| API
    API -->|Route Handling| Routes
    
    %% API to Services
    Routes -->|Process Documents| RAG
    Routes -->|Query| RAG
    Routes -->|Session Management| Conv
    
    %% Service interactions
    RAG -->|Process Text| Doc
    RAG -->|Store Embeddings| Vector
    RAG -->|Generate Embeddings & Responses| AzureAI
    RAG -->|Manage Conversation| Conv
    Doc -->|Generate Embeddings| AzureAI
    Vector -->|Store/Retrieve Vectors| Qdrant
    Vector -->|Generate Embeddings| AzureAI
    
    %% Storage interactions
    Doc -->|Read/Write Files| FileSystem
```

## Component Descriptions

### Frontend Layer
- **Streamlit UI**: Provides a user-friendly interface for document upload, chat interactions, and profile matching.

### API Layer
- **FastAPI**: High-performance web framework for building APIs.
- **API Routes**: Endpoints for session management, document processing, querying, and profile matching.

### Core Services
- **RAG Service**: Orchestrates the RAG workflow, connecting document processing, vector storage, and response generation.
- **Conversation Service**: Manages chat sessions and conversation history.
- **Document Processor**: Handles document reading, text extraction, and chunking.
- **Vector Store**: Manages vector embeddings storage and retrieval.
- **Azure OpenAI Service**: Interfaces with Azure OpenAI for embeddings and chat completions.

### Storage
- **Qdrant Vector DB**: Stores and indexes document embeddings for semantic search.
- **File System**: Stores uploaded documents.

## RAG Workflow

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant RAG as RAG Service
    participant Doc as Document Processor
    participant Vector as Vector Store
    participant AzureAI as Azure OpenAI
    participant Qdrant as Qdrant DB
    
    %% Document Processing Flow
    User->>UI: Upload Document
    UI->>API: POST /upload
    API->>RAG: process_and_store_document()
    RAG->>Doc: process_document()
    Doc->>Doc: read_document()
    Doc->>Doc: split_text()
    Doc-->>RAG: chunks, metadatas
    RAG->>AzureAI: generate_embeddings()
    AzureAI-->>RAG: embeddings
    RAG->>Vector: add_documents()
    Vector->>Qdrant: upsert()
    Qdrant-->>Vector: success
    Vector-->>RAG: document_ids
    RAG-->>API: success
    API-->>UI: success message
    UI-->>User: Document processed
    
    %% Query Flow
    User->>UI: Ask Question
    UI->>API: POST /query
    API->>RAG: query()
    RAG->>Conv: get_conversation_history()
    Conv-->>RAG: conversation_history
    RAG->>AzureAI: contextualize_query()
    AzureAI-->>RAG: contextualized_query
    RAG->>Vector: search()
    Vector->>AzureAI: generate_embeddings()
    AzureAI-->>Vector: query_embedding
    Vector->>Qdrant: search()
    Qdrant-->>Vector: search_results
    Vector-->>RAG: texts, metadatas, scores
    RAG->>AzureAI: generate_rag_response()
    AzureAI-->>RAG: response
    RAG->>Conv: add_message()
    RAG-->>API: response, sources
    API-->>UI: response, sources
    UI-->>User: Display response with sources
```

## Profile Matching Workflow

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant RAG as RAG Service
    participant Doc as Document Processor
    
    User->>UI: Select Profiles & SOW
    User->>UI: Click "Match Profiles"
    UI->>API: POST /match
    API->>RAG: match_profiles_to_sow()
    RAG->>Doc: read_document() for SOW
    Doc-->>RAG: sow_text
    RAG->>Doc: read_document() for Profiles
    Doc-->>RAG: profile_texts
    RAG->>Doc: extract_requirements_from_sow()
    Doc-->>RAG: sow_requirements
    RAG->>Doc: extract_skills_from_text()
    Doc-->>RAG: profile_skills
    RAG->>Doc: calculate_match_score()
    Doc-->>RAG: matches
    RAG-->>API: matches
    API-->>UI: matches
    UI-->>User: Display match results
```

## Deployment Architecture

```mermaid
graph TD
    subgraph "Docker Environment"
        subgraph "Frontend Container"
            UI[Streamlit UI]
        end
        
        subgraph "API Container"
            API[FastAPI]
            Services[Core Services]
        end
        
        subgraph "Qdrant Container"
            Qdrant[(Qdrant Vector DB)]
        end
        
        Volume[(Shared Volume)]
    end
    
    subgraph "External Services"
        Azure[Azure OpenAI]
    end
    
    UI -->|HTTP| API
    API -->|Store/Retrieve| Qdrant
    API -->|Read/Write Files| Volume
    API -->|API Calls| Azure
```

## Key Features

1. **Document Processing**
   - Support for PDF, DOCX, and TXT files
   - Intelligent text chunking with configurable size and overlap

2. **Semantic Search**
   - Vector embeddings using Azure OpenAI
   - Efficient similarity search with Qdrant

3. **Conversation Management**
   - Session-based conversations
   - Follow-up question handling with context

4. **Profile Matching**
   - Skill extraction and matching
   - Scoring based on requirement alignment

5. **User Interface**
   - Document upload and management
   - Interactive chat with source references
   - Profile matching visualization



![alt text](<Screenshot 2025-06-16 at 12.33.15 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.33.11 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.33.07 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.33.03 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.32.59 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.32.53 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.32.48 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.32.40 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.32.36 AM.png>) ![alt text](<Screenshot 2025-06-16 at 12.32.31 AM.png>)
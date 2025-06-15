from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import shutil
from pydantic import BaseModel

from app.core.config import settings
from app.services.rag_service import rag_service
from app.services.conversation import conversation_service

router = APIRouter()

class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    query: str
    session_id: str
    top_k: int = 3

class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    query: str
    contextualized_query: str
    response: str
    sources: List[Dict[str, Any]]

class SessionResponse(BaseModel):
    """Response model for session creation."""
    session_id: str

class MatchRequest(BaseModel):
    """Request model for matching profiles to SOW."""
    profile_ids: List[str]
    sow_id: str

class MatchResponse(BaseModel):
    """Response model for profile matching."""
    matches: List[Dict[str, Any]]

class DocumentResponse(BaseModel):
    """Response model for document processing."""
    success: bool
    message: str
    document_id: Optional[str] = None

@router.post("/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new conversation session."""
    session_id = conversation_service.create_session()
    return {"session_id": session_id}

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload and process a document.
    
    Args:
        file: The document file
        background_tasks: Background tasks runner
        
    Returns:
        Document processing result
    """
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the document (can be done in background for large files)
        if background_tasks:
            background_tasks.add_task(rag_service.process_and_store_document, file_path)
            return {
                "success": True,
                "message": f"Document {file.filename} uploaded and processing started",
                "document_id": file.filename
            }
        else:
            success = rag_service.process_and_store_document(file_path)
            if success:
                return {
                    "success": True,
                    "message": f"Document {file.filename} uploaded and processed successfully",
                    "document_id": file.filename
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to process document {file.filename}",
                    "document_id": file.filename
                }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system.
    
    Args:
        request: Query request
        
    Returns:
        Query response
    """
    try:
        result = rag_service.query(
            query=request.query,
            session_id=request.session_id,
            top_k=request.top_k
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying RAG system: {str(e)}")

@router.post("/match", response_model=MatchResponse)
async def match_profiles(request: MatchRequest):
    """
    Match profiles to a Statement of Work.
    
    Args:
        request: Match request
        
    Returns:
        Match response
    """
    try:
        # Get file paths from IDs
        profile_file_paths = [
            os.path.join(settings.UPLOAD_DIR, profile_id)
            for profile_id in request.profile_ids
        ]
        
        sow_file_path = os.path.join(settings.UPLOAD_DIR, request.sow_id)
        
        # Match profiles to SOW
        matches = rag_service.match_profiles_to_sow(
            profile_file_paths=profile_file_paths,
            sow_file_path=sow_file_path
        )
        
        return {"matches": matches}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching profiles: {str(e)}")

@router.get("/documents")
async def list_documents():
    """
    List all uploaded documents.
    
    Returns:
        List of documents
    """
    try:
        documents = []
        
        if os.path.exists(settings.UPLOAD_DIR):
            for filename in os.listdir(settings.UPLOAD_DIR):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in ['.txt', '.pdf', '.docx']:
                        documents.append({
                            "id": filename,
                            "name": filename,
                            "type": ext[1:],  # Remove the dot
                            "size": os.path.getsize(file_path)
                        })
        
        return {"documents": documents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document.
    
    Args:
        document_id: The document ID
        
    Returns:
        Deletion result
    """
    try:
        file_path = os.path.join(settings.UPLOAD_DIR, document_id)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
        
        os.remove(file_path)
        
        return {"success": True, "message": f"Document {document_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a conversation session.
    
    Args:
        session_id: The session ID
        
    Returns:
        Deletion result
    """
    try:
        success = conversation_service.delete_session(session_id)
        
        if success:
            return {"success": True, "message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

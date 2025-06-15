import os
import PyPDF2
import docx
from typing import List, Dict, Any, Tuple
import re

from app.core.config import settings

def read_text_file(file_path: str) -> str:
    """Read content from a text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_pdf_file(file_path: str) -> str:
    """Read content from a PDF file."""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:  # Some PDF pages might not have extractable text
                text += page_text + "\n\n"
    return text

def read_docx_file(file_path: str) -> str:
    """Read content from a Word document."""
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        if para.text:
            full_text.append(para.text)
    return '\n'.join(full_text)

def read_document(file_path: str) -> str:
    """Read document content based on file extension."""
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == '.txt':
        return read_text_file(file_path)
    elif file_extension == '.pdf':
        return read_pdf_file(file_path)
    elif file_extension == '.docx':
        return read_docx_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def split_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    """
    Split text into chunks while preserving sentence boundaries.
    
    Args:
        text: The text to split
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    
    if chunk_overlap is None:
        chunk_overlap = settings.CHUNK_OVERLAP
    
    # Clean the text
    text = text.replace('\n', ' ').strip()
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Ensure proper sentence ending
        if not any(sentence.endswith(end) for end in ['.', '!', '?']):
            sentence += '.'

        sentence_size = len(sentence)

        # Check if adding this sentence would exceed chunk size
        if current_size + sentence_size > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            
            # Keep some sentences for overlap
            overlap_size = 0
            overlap_sentences = []
            
            for s in reversed(current_chunk):
                if overlap_size + len(s) <= chunk_overlap:
                    overlap_sentences.insert(0, s)
                    overlap_size += len(s) + 1  # +1 for the space
                else:
                    break
            
            current_chunk = overlap_sentences + [sentence]
            current_size = sum(len(s) for s in current_chunk) + len(current_chunk) - 1  # -1 because no space after last sentence
        else:
            current_chunk.append(sentence)
            current_size += sentence_size + (1 if current_chunk else 0)  # +1 for the space

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def process_document(file_path: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Process a document and prepare it for vector storage.
    
    Args:
        file_path: Path to the document
        
    Returns:
        Tuple of (chunks, metadatas)
    """
    try:
        # Read the document
        content = read_document(file_path)

        # Split into chunks
        chunks = split_text(content)

        # Prepare metadata
        file_name = os.path.basename(file_path)
        metadatas = [
            {
                "source": file_name,
                "chunk_index": i,
                "file_path": file_path
            } 
            for i in range(len(chunks))
        ]

        return chunks, metadatas
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return [], []

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from text using simple keyword matching.
    In a production system, this would use NER or more sophisticated techniques.
    
    Args:
        text: The text to extract skills from
        
    Returns:
        List of extracted skills
    """
    # This is a simplified implementation
    # In a real system, you would use NER or ML-based extraction
    common_skills = [
        "python", "javascript", "java", "c++", "c#", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
        "machine learning", "deep learning", "nlp", "computer vision",
        "data science", "data analysis", "data engineering", "devops",
        "project management", "agile", "scrum", "product management"
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill in text_lower:
            found_skills.append(skill)
    
    return found_skills

def extract_requirements_from_sow(sow_text: str) -> List[str]:
    """
    Extract requirements from Statement of Work.
    
    Args:
        sow_text: The SOW text
        
    Returns:
        List of extracted requirements/skills
    """
    # For simplicity, we'll use the same skill extraction
    # In a real system, this would be more sophisticated
    return extract_skills_from_text(sow_text)

def calculate_match_score(profile_skills: List[str], sow_requirements: List[str]) -> float:
    """
    Calculate match score between profile skills and SOW requirements.
    
    Args:
        profile_skills: List of skills from profile
        sow_requirements: List of requirements from SOW
        
    Returns:
        Match score between 0 and 1
    """
    if not sow_requirements:
        return 0.0
    
    matches = set(profile_skills).intersection(set(sow_requirements))
    return len(matches) / len(sow_requirements)

def get_matching_skills(profile_skills: List[str], sow_requirements: List[str]) -> List[str]:
    """
    Get the list of matching skills between profile and SOW.
    
    Args:
        profile_skills: List of skills from profile
        sow_requirements: List of requirements from SOW
        
    Returns:
        List of matching skills
    """
    return list(set(profile_skills).intersection(set(sow_requirements)))

def match_resources_to_project(profiles: List[Dict[str, Any]], sow_text: str) -> List[Dict[str, Any]]:
    """
    Match resources to project based on skills.
    
    Args:
        profiles: List of profile dictionaries with text and name
        sow_text: The SOW text
        
    Returns:
        List of matches with scores
    """
    sow_requirements = extract_requirements_from_sow(sow_text)
    matches = []
    
    for profile in profiles:
        skills = extract_skills_from_text(profile["text"])
        match_score = calculate_match_score(skills, sow_requirements)
        matching_skills = get_matching_skills(skills, sow_requirements)
        
        matches.append({
            "name": profile["name"],
            "match_score": match_score,
            "matching_skills": matching_skills,
            "all_skills": skills
        })
    
    return sorted(matches, key=lambda x: x["match_score"], reverse=True)

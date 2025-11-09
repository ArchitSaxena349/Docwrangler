from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.models import DocumentChunk, DocumentType

class BaseDocumentProcessor(ABC):
    """Base class for document processors"""
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract text content from document"""
        pass
    
    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from document"""
        pass
    
    def chunk_document(self, text: str, document_id: str, chunk_size: int = 1000, 
                      chunk_overlap: int = 200) -> List[DocumentChunk]:
        """Split document into chunks for processing"""
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:
                    end = start + break_point + 1
                    chunk_text = text[start:end]
            
            chunk = DocumentChunk(
                chunk_id=f"{document_id}_chunk_{chunk_id}",
                document_id=document_id,
                content=chunk_text.strip(),
                metadata={
                    "chunk_index": chunk_id,
                    "start_position": start,
                    "end_position": end
                }
            )
            chunks.append(chunk)
            
            start = end - chunk_overlap
            chunk_id += 1
            
        return chunks
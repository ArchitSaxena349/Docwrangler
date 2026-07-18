from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.core.models import DocumentChunk, DocumentType

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
        if chunk_size <= 0:
            chunk_size = 1000
        if chunk_overlap >= chunk_size or chunk_overlap < 0:
            chunk_overlap = chunk_size // 5  # default to 20% of chunk size to avoid loops

        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # Try to break at logical layout boundary (double newline, single newline, period)
            if end < len(text):
                last_double_newline = chunk_text.rfind('\n\n')
                if last_double_newline > chunk_size // 2:
                    end = start + last_double_newline + 2
                    chunk_text = text[start:end]
                else:
                    last_newline = chunk_text.rfind('\n')
                    if last_newline > chunk_size // 2:
                        end = start + last_newline + 1
                        chunk_text = text[start:end]
                    else:
                        last_period = chunk_text.rfind('.')
                        if last_period > chunk_size // 2:
                            end = start + last_period + 1
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
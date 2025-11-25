import os
import uuid
from pathlib import Path
from typing import List

from src.document_processor.processor_factory import ProcessorFactory
from src.retrieval.vector_store import VectorStore
from core.config import Config

class DocumentService:
    """Service for document processing and management"""
    
    def __init__(self):
        self.vector_store = VectorStore()
    
    async def process_document(self, file_path: str) -> str:
        """Process a document and add it to the vector store"""
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Get appropriate processor
            file_extension = Path(file_path).suffix
            processor = ProcessorFactory.get_processor_by_extension(file_extension)
            
            # Extract text and metadata
            text = processor.extract_text(file_path)
            metadata = processor.extract_metadata(file_path)
            
            # Add document ID to metadata
            metadata['document_id'] = document_id
            metadata['original_filename'] = Path(file_path).name
            
            # Chunk the document
            chunks = processor.chunk_document(
                text=text,
                document_id=document_id,
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP
            )
            
            # Add metadata to each chunk
            for chunk in chunks:
                chunk.metadata.update(metadata)
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            
            return document_id
            
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    async def delete_document(self, document_id: str) -> None:
        """Delete a document from the vector store"""
        try:
            self.vector_store.delete_document(document_id)
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
    
    def list_documents(self) -> List[str]:
        """List all document IDs in the system"""
        try:
            return self.vector_store.list_documents()
        except Exception as e:
            raise Exception(f"Error listing documents: {str(e)}")
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        try:
            return self.vector_store.get_document_count()
        except Exception as e:
            raise Exception(f"Error getting document count: {str(e)}")
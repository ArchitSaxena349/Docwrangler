from typing import Dict, Type
from .base import BaseDocumentProcessor
from .pdf_processor import PDFProcessor
from .docx_processor import DocxProcessor
from .email_processor import EmailProcessor
from core.models import DocumentType

class ProcessorFactory:
    """Factory for creating document processors"""
    
    _processors: Dict[DocumentType, Type[BaseDocumentProcessor]] = {
        DocumentType.PDF: PDFProcessor,
        DocumentType.DOCX: DocxProcessor,
        DocumentType.EMAIL: EmailProcessor,
    }
    
    @classmethod
    def get_processor(cls, document_type: DocumentType) -> BaseDocumentProcessor:
        """Get appropriate processor for document type"""
        processor_class = cls._processors.get(document_type)
        if not processor_class:
            raise ValueError(f"No processor available for document type: {document_type}")
        
        return processor_class()
    
    @classmethod
    def get_processor_by_extension(cls, file_extension: str) -> BaseDocumentProcessor:
        """Get processor based on file extension"""
        extension_mapping = {
            '.pdf': DocumentType.PDF,
            '.docx': DocumentType.DOCX,
            '.doc': DocumentType.DOCX,
            '.eml': DocumentType.EMAIL,
            '.msg': DocumentType.EMAIL,
        }
        
        document_type = extension_mapping.get(file_extension.lower())
        if not document_type:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        return cls.get_processor(document_type)
import PyPDF2
from typing import Dict, Any
from .base import BaseDocumentProcessor

class PDFProcessor(BaseDocumentProcessor):
    """PDF document processor"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
        
        return text.strip()
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {"file_type": "pdf", "file_path": file_path}
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.metadata:
                    metadata.update({
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                        "creation_date": str(pdf_reader.metadata.get("/CreationDate", "")),
                    })
                
                metadata["page_count"] = len(pdf_reader.pages)
                
        except Exception as e:
            metadata["extraction_error"] = str(e)
        
        return metadata
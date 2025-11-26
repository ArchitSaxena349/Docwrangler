from typing import Dict, Any, List
from .base import BaseDocumentProcessor

class TextProcessor(BaseDocumentProcessor):
    """Processor for plain text files"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from .txt file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from .txt file"""
        import os
        from datetime import datetime
        
        stats = os.stat(file_path)
        return {
            'file_size': stats.st_size,
            'creation_date': datetime.fromtimestamp(stats.st_ctime).isoformat(),
            'modification_date': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'file_type': 'text/plain'
        }

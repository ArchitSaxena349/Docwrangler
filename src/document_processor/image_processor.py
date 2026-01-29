from typing import Dict, Any
from .base import BaseDocumentProcessor
from google import genai
from core.config import Config
import PIL.Image

class ImageProcessor(BaseDocumentProcessor):
    """Processor for image files (JPG, PNG) using Gemini Vision"""
    
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model = 'gemini-1.5-flash'
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from image using Gemini Vision"""
        try:
            img = PIL.Image.open(file_path)
            
            prompt = """
            You are an expert OCR system for insurance documents. 
            Transcribe the text from this image exactly as it appears. 
            Preserve the structure, headings, and key details like policy numbers, names, and coverage limits.
            If the image is blurry or unreadable, state that clearly.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, img]
            )
            return response.text
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from image file"""
        import os
        from datetime import datetime
        
        stats = os.stat(file_path)
        return {
            'file_size': stats.st_size,
            'creation_date': datetime.fromtimestamp(stats.st_ctime).isoformat(),
            'modification_date': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'file_type': 'image'
        }

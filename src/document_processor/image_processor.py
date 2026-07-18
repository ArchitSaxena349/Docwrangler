import base64
import mimetypes
from typing import Dict, Any
from .base import BaseDocumentProcessor
from groq import Groq
from src.core.config import Config

class ImageProcessor(BaseDocumentProcessor):
    """Processor for image files (JPG, PNG) using Groq Vision"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_VISION_MODEL
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from image using Groq Vision"""
        try:
            prompt = """
            You are an expert OCR system for insurance documents. 
            Transcribe the text from this image exactly as it appears. 
            Preserve the structure, headings, and key details like policy numbers, names, and coverage limits.
            If the image is blurry or unreadable, state that clearly.
            """
            
            # Read and encode image in base64
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "image/jpeg"
                
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{encoded_string}"
                                }
                            }
                        ]
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}") from e
    
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

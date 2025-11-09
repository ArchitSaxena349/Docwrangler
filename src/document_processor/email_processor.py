import email
from email.mime.text import MIMEText
from typing import Dict, Any
from .base import BaseDocumentProcessor

class EmailProcessor(BaseDocumentProcessor):
    """Email document processor"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from email file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                msg = email.message_from_file(file)
            
            text = ""
            
            # Extract headers
            text += f"From: {msg.get('From', '')}\n"
            text += f"To: {msg.get('To', '')}\n"
            text += f"Subject: {msg.get('Subject', '')}\n"
            text += f"Date: {msg.get('Date', '')}\n\n"
            
            # Extract body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        text += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                text += msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error processing email: {str(e)}")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from email"""
        metadata = {"file_type": "email", "file_path": file_path}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                msg = email.message_from_file(file)
            
            metadata.update({
                "from": msg.get('From', ''),
                "to": msg.get('To', ''),
                "subject": msg.get('Subject', ''),
                "date": msg.get('Date', ''),
                "message_id": msg.get('Message-ID', ''),
                "content_type": msg.get_content_type()
            })
            
        except Exception as e:
            metadata["extraction_error"] = str(e)
        
        return metadata
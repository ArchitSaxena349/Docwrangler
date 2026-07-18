import os
import asyncio
from pathlib import Path
from src.services.document_service import DocumentService
from src.api.dependencies import init_services, get_document_service
from src.utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

async def seed():
    setup_logging()
    init_services()
    service = get_document_service()
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("Data directory not found.")
        return
        
    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in data/.")
        return
        
    print(f"Found {len(pdf_files)} policy documents in data/. Indexing them...")
    
    for pdf in pdf_files:
        print(f"Processing {pdf.name}...")
        try:
            # Check if this document is already in the system
            # Since document list matches original filename metadata, we can check list_documents
            existing_docs = service.list_documents()
            # Wait, list_documents returns document IDs. Let's index them normally.
            doc_id = await service.process_document(str(pdf))
            print(f"Successfully indexed {pdf.name}. ID: {doc_id}")
        except Exception as e:
            print(f"Failed to index {pdf.name}: {e}")
            
if __name__ == "__main__":
    asyncio.run(seed())

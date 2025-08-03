from langchain.docstore.document import Document
import re

def smart_chunk(text, metadata={}, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(Document(page_content=chunk, metadata=metadata))
    return chunks

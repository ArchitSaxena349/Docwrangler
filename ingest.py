from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from utils.parsers import extract_text
from utils.chunker import smart_chunk
import os

doc_dir = "data/policy_docs"
chunks = []

for file in os.listdir(doc_dir):
    path = os.path.join(doc_dir, file)
    text = extract_text(path)
    doc_chunks = smart_chunk(text, metadata={"source": file})
    chunks.extend(doc_chunks)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(chunks, embeddings)
db.save_local("vectorstore/faiss_index")

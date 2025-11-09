#!/usr/bin/env python3
"""
Test with local embeddings - no OpenAI API needed for embeddings
"""
import os
import asyncio
import time
from pathlib import Path
import PyPDF2
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import re
import json

class LocalEmbeddingProcessor:
    def __init__(self):
        print("🔧 Initializing local embedding model...")
        # Use a lightweight model for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB (use centralized data/vector_store location)
        self.client = chromadb.PersistentClient(path=os.path.join("data", "vector_store", "local_chroma_db"))
        self.collection = self.client.get_or_create_collection(
            name="insurance_docs",
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ Local embedding system ready")
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
        """Split text into chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > start + chunk_size // 2:
                    end = start + last_period + 1
                    chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - overlap
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> str:
        """Process a PDF and add to vector store"""
        print(f"📄 Processing: {pdf_path}")
        
        # Extract text
        text = self.extract_pdf_text(pdf_path)
        if not text:
            return None
        
        print(f"   Extracted {len(text):,} characters")
        
        # Create chunks
        chunks = self.chunk_text(text)
        print(f"   Created {len(chunks)} chunks")
        
        # Generate embeddings
        print("   Generating embeddings...")
        embeddings = self.embedding_model.encode(chunks)
        
        # Prepare data for ChromaDB
        doc_id = Path(pdf_path).stem
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"document": doc_id, "chunk_index": i, "source_file": pdf_path} 
                    for i in range(len(chunks))]
        
        # Add to collection
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(chunks)} chunks to vector store")
        return doc_id
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        print(f"🔍 Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        search_results = []
        for i in range(len(results['ids'][0])):
            similarity = 1 - results['distances'][0][i]  # Convert distance to similarity
            result = {
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity': similarity
            }
            search_results.append(result)
        
        print(f"   Found {len(search_results)} relevant sections")
        return search_results
    
    def analyze_query_with_openai(self, query: str, context: str) -> Dict:
        """Analyze query using OpenAI (if available)"""
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            return self.analyze_query_locally(query, context)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            prompt = f"""
            Based on this insurance document context:
            
            {context}
            
            Answer this query: {query}
            
            Provide a JSON response with:
            - decision: "approved", "rejected", "pending", or "insufficient_info"
            - amount: numeric amount if applicable
            - justification: explanation with specific references
            - confidence: 0.0 to 1.0
            
            Return only valid JSON.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            result['method'] = 'openai'
            return result
            
        except Exception as e:
            print(f"   OpenAI analysis failed: {e}")
            return self.analyze_query_locally(query, context)
    
    def analyze_query_locally(self, query: str, context: str) -> Dict:
        """Local rule-based analysis"""
        print("   Using local analysis...")
        
        query_lower = query.lower()
        context_lower = context.lower()
        
        # Extract age
        age_match = re.search(r'(\d+)[-\s]*(?:year|yr|y)[-\s]*old|(\d+)[MF]', query)
        age = int(age_match.group(1) or age_match.group(2)) if age_match else None
        
        # Extract procedure
        procedures = ['surgery', 'treatment', 'procedure', 'operation', 'cardiac', 'knee', 'dental', 'maternity']
        detected_procedure = None
        for proc in procedures:
            if proc in query_lower:
                detected_procedure = proc
                break
        
        # Find amounts in context
        amount_patterns = [
            r'₹\s*(\d+(?:,\d+)*)',
            r'rs\.?\s*(\d+(?:,\d+)*)',
            r'(\d+)\s*lakh',
            r'(\d+)\s*crore'
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.finditer(pattern, context_lower)
            for match in matches:
                try:
                    if 'lakh' in match.group(0):
                        amount = float(match.group(1).replace(',', '')) * 100000
                    elif 'crore' in match.group(0):
                        amount = float(match.group(1).replace(',', '')) * 10000000
                    else:
                        amount = float(match.group(1).replace(',', ''))
                    amounts.append(amount)
                except:
                    pass
        
        # Find waiting periods
        waiting_patterns = [
            r'(\d+)\s*(?:months?|days?|years?)\s*waiting',
            r'waiting\s*period\s*(?:of\s*)?(\d+)'
        ]
        
        waiting_periods = []
        for pattern in waiting_patterns:
            matches = re.finditer(pattern, context_lower)
            for match in matches:
                waiting_periods.append(match.group(0))
        
        # Simple decision logic
        decision = "insufficient_info"
        confidence = 0.3
        justification = "Limited information available for decision."
        amount = None
        
        if detected_procedure and amounts:
            max_amount = max(amounts)
            if 'surgery' in detected_procedure or 'cardiac' in detected_procedure:
                decision = "likely_approved"
                confidence = 0.7
                amount = max_amount
                justification = f"{detected_procedure.title()} is typically covered. Maximum amount found: ₹{max_amount:,.0f}"
            elif 'dental' in detected_procedure:
                decision = "check_waiting_period"
                confidence = 0.6
                justification = "Dental procedures may have waiting periods. Check policy terms."
        
        if waiting_periods:
            justification += f" Waiting periods found: {', '.join(waiting_periods[:2])}"
        
        return {
            'decision': decision,
            'amount': amount,
            'justification': justification,
            'confidence': confidence,
            'method': 'local',
            'detected_age': age,
            'detected_procedure': detected_procedure,
            'amounts_found': len(amounts),
            'waiting_periods': len(waiting_periods)
        }
    
    def process_query(self, query: str) -> Dict:
        """Process a complete query"""
        print(f"\n{'='*60}")
        print(f"PROCESSING QUERY: {query}")
        print(f"{'='*60}")
        
        # Search for relevant documents
        search_results = self.search_documents(query)
        
        if not search_results:
            return {
                'query': query,
                'decision': 'no_relevant_docs',
                'justification': 'No relevant documents found',
                'confidence': 0.0
            }
        
        # Combine top results for context
        context = "\n\n".join([result['content'] for result in search_results[:3]])
        
        # Show search results
        print(f"\n📋 TOP SEARCH RESULTS:")
        for i, result in enumerate(search_results[:3], 1):
            print(f"   {i}. Similarity: {result['similarity']:.3f}")
            print(f"      Source: {result['metadata']['document']}")
            print(f"      Content: {result['content'][:150]}...")
        
        # Analyze query
        analysis = self.analyze_query_with_openai(query, context)
        
        # Display results
        print(f"\n🤖 ANALYSIS RESULT:")
        print(f"   Method: {analysis.get('method', 'unknown')}")
        print(f"   Decision: {analysis['decision']}")
        print(f"   Confidence: {analysis['confidence']:.1%}")
        if analysis.get('amount'):
            print(f"   Amount: ₹{analysis['amount']:,.0f}")
        print(f"   Justification: {analysis['justification']}")
        
        # Add search results to response
        analysis['query'] = query
        analysis['search_results'] = search_results[:3]
        
        return analysis

async def main():
    """Main test function"""
    print("🏥 Local Embedding Insurance PDF Test")
    print("="*50)
    
    processor = LocalEmbeddingProcessor()
    
    # Find PDF files in data directory
    data_dir = Path('../data')
    if not data_dir.exists():
        data_dir = Path('./data')  # Try current directory structure
    
    if data_dir.exists():
        pdf_files = [str(data_dir / f) for f in os.listdir(data_dir) if f.endswith('.pdf')]
    else:
        # Fallback to current directory
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found")
        print("💡 Expected location: data/ directory")
        print("💡 Current search paths:")
        if data_dir.exists():
            print(f"   - {data_dir.absolute()}")
        print(f"   - {Path('.').absolute()}")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF files")
    
    # Process all PDFs
    processed_docs = []
    for pdf_file in pdf_files:
        doc_id = processor.process_pdf(pdf_file)
        if doc_id:
            processed_docs.append(doc_id)
    
    print(f"\n✅ Successfully processed {len(processed_docs)} documents")
    
    # Test queries
    test_queries = [
        "46-year-old male, knee surgery, 3-month policy",
        "What is the maximum coverage amount for cardiac surgery?",
        "Waiting period for dental treatment",
        "Maternity benefits and coverage",
        "Emergency treatment coverage limits",
        "Age limit for policy renewal",
        "Pre-existing condition waiting period"
    ]
    
    print(f"\n🔍 TESTING QUERIES")
    print("="*50)
    
    results = []
    for query in test_queries:
        result = processor.process_query(query)
        results.append(result)
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("="*50)
    print(f"Documents processed: {len(processed_docs)}")
    print(f"Queries tested: {len(results)}")
    
    decision_counts = {}
    for result in results:
        decision = result['decision']
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
    
    print(f"Decision breakdown:")
    for decision, count in decision_counts.items():
        print(f"  {decision}: {count}")
    
    print(f"\n🎉 Local embedding test completed!")

if __name__ == "__main__":
    asyncio.run(main())
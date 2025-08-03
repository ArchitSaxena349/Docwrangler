# LLM Document Wrangler

A FastAPI-based application that processes insurance policy documents using vector search and OpenAI for intelligent query processing.

## Features

- **Document Processing**: Supports PDF, DOCX, MSG, EML, and TXT files
- **Vector Search**: Uses FAISS for semantic document search
- **LLM Integration**: Leverages OpenAI GPT-4 for intelligent responses
- **REST API**: FastAPI endpoint for document analysis
- **Smart Chunking**: Intelligent text chunking for better vector storage

## Project Structure

```
LLM_docwrangler/
├── main.py              # FastAPI application entry point
├── query.py             # Query processing and vector search
├── ingest.py            # Document ingestion and vectorstore creation
├── dfd.py               # Direct OpenAI testing script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── data/
│   └── policy_docs/     # Sample insurance policy documents
├── utils/
│   ├── parsers.py       # Document parsing utilities
│   ├── chunker.py       # Text chunking utilities
│   └── llm_utils.py     # OpenAI integration utilities
└── vectorstore/
    └── faiss_index/     # FAISS vector database files
```

## Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy your OpenAI API key to the `.env` file
   - The `.env` file should contain:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

4. **Run document ingestion** (if needed):
   ```bash
   python ingest.py
   ```

5. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

## API Usage

### Analyze Document Query

**POST** `/analyze`

**Request Body**:
```json
{
  "query": "Is knee surgery covered for a 46-year-old in a 3-month-old policy?"
}
```

**Response**:
```json
{
  "result": {
    "decision": "covered/not_covered",
    "amount": "payout_amount",
    "justification": {
      "summary": "explanation",
      "referenced_clauses": ["clause1", "clause2"]
    }
  }
}
```

## Components

### Core Files

- **main.py**: FastAPI application with `/analyze` endpoint
- **query.py**: Handles query processing using vector search and LLM
- **ingest.py**: Creates vector embeddings from policy documents

### Utilities

- **parsers.py**: Extracts text from various document formats
- **chunker.py**: Splits documents into searchable chunks
- **llm_utils.py**: OpenAI integration for entity extraction and decision making

## Dependencies

- FastAPI & Uvicorn for web framework
- LangChain & HuggingFace for embeddings
- FAISS for vector search
- OpenAI for language model
- Document parsing libraries (pdfplumber, python-docx, extract-msg)

## Security

- API keys are stored in environment variables
- `.env` file should never be committed to version control
- Add `.env` to your `.gitignore` file

## Development

To add new document types:
1. Extend `parsers.py` with new extraction logic
2. Update `ingest.py` to handle new file types
3. Test with sample documents

## License

[Add your license information here]
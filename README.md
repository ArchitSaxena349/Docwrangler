# 🏥 LLM DocWrangler — Insurance Document Processing

A production-ready FastAPI application that extracts, indexes, and answers questions about insurance documents using Google's Gemini API and local embeddings.

## 🚀 Quick Start

### Windows (Lightweight Mode)
This mode avoids heavy dependency build issues on Windows.

1. **Create Virtual Environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install Minimal Dependencies:**
   ```powershell
   pip install -r requirements-minimal.txt
   pip install python-docx pypdf2 python-multipart
   ```

3. **Set Environment Variables:**
   Create a `.env` file:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   APP_API_KEY=your_secret_api_key  # Optional: for API security
   LOG_LEVEL=INFO
   ```

4. **Run Server:**
   ```powershell
   uvicorn main:app --reload
   ```

### Linux / Mac / Production (Full Features)
Use this for deployment (e.g., Render) to enable Vector Store features.

1. **Install Full Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Run Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access the UI at `http://localhost:5173`.

## ☁️ Deployment (Render)

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `GEMINI_API_KEY`: Your Google Gemini API Key
  - `GEMINI_MODEL`: `gemini-1.5-flash` (default)
  - `APP_API_KEY`: (Optional) Secret key for protecting `/api/*` endpoints
  - `PYTHON_VERSION`: `3.11.9` (Required for compatibility)

## 📂 Project Structure

- `main.py`: FastAPI application entry point.
- `src/`: Core application source code.
  - `api/`: Routes, middleware, and security.
  - `services/`: Business logic (QueryService, DocumentService).
  - `retrieval/`: Vector store implementation (resilient to missing deps).
- `core/`: Configuration and Pydantic models.
- `tests/`: Comprehensive test suite.

## 🔌 API Endpoints

### Webhooks (Backward Compatible)
- `POST /webhook/query`: Process natural language queries.
- `POST /webhook/insurance-claim`: Specialized claim processing.
- `POST /webhook/document-upload`: Upload documents.

### REST API (Protected)
Requires `x-api-key` header if `APP_API_KEY` is set.
- `POST /api/query`: Full query processing.
- `POST /api/upload`: Upload and index documents.
- `GET /api/documents`: List indexed documents.

## 🧪 Testing

Run the full test suite:
```bash
pytest tests/ -v
```

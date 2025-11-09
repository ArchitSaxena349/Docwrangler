# LLM Document Processing System

A clean, organized system that uses Large Language Models to process natural language queries and retrieve relevant information from insurance documents.

## 🏗️ Project Structure

```
├── core/                   # Core configuration and models
│   ├── config.py          # Configuration settings
│   ├── models.py          # Data models
│   └── requirements.txt   # Dependencies
├── src/                   # Source code
│   ├── document_processor/ # PDF/DOCX processing
│   ├── query_engine/      # Natural language processing
│   ├── retrieval/         # Vector search and retrieval
│   ├── decision_engine/   # AI decision making
│   ├── services/          # Business logic services
│   └── api/              # REST API endpoints
├── webhook/               # Webhook server and API
│   ├── basic_webhook_server.py    # Simple webhook server
│   ├── webhook_api_documentation.json # API docs
│   └── webhook_test_page.html     # Web test interface
├── tests/                 # Test scripts
│   ├── local_embedding_test.py    # Local AI testing
│   └── offline_pdf_analyzer.py    # PDF analysis without API
├── docs/                  # Documentation
│   ├── README.md          # This file
│   └── SHARE_WITH_WEBSITE.md # Webhook sharing guide
├── data/                  # Insurance policy documents
│   └── *.pdf             # 6 real insurance policies
├── config/                # Configuration files
│   └── .env.example      # Environment template
└── backup_before_clean/   # Backup of original files
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
cp config/.env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Install Dependencies
```bash
pip install -r core/requirements.txt
```

### 3. Run Webhook Server
```bash
python webhook/basic_webhook_server.py
```

### 4. Test Locally
```bash
python tests/local_embedding_test.py
```

## 🌐 Webhook API

The system provides a webhook API for processing insurance queries:

- **Health Check**: `GET /webhook/health`
- **Process Query**: `POST /webhook/query`
- **Insurance Claim**: `POST /webhook/insurance-claim`
- **Document Upload**: `POST /webhook/document-upload`

See `webhook/webhook_api_documentation.json` for complete API details.

## 📄 Data Sources

The system processes 6 real insurance policies:
- Bajaj Allianz Health Insurance
- Cholamandalam Health Insurance  
- Edelweiss Health Insurance
- HDFC Health Insurance
- ICICI Health Insurance
- National Insurance Arogya Sanjeevani

## 🧪 Testing

- **Local Testing**: `python tests/local_embedding_test.py`
- **Offline Analysis**: `python tests/offline_pdf_analyzer.py`
- **Web Interface**: Open `webhook/webhook_test_page.html`

## 🔧 Features

- ✅ AI-powered document analysis
- ✅ Natural language query processing
- ✅ Structured claim evaluation
- ✅ Real-time decision making
- ✅ Confidence scoring
- ✅ CORS-enabled webhook API
- ✅ Multiple insurance policy support

## 📚 Documentation

- API Documentation: `webhook/webhook_api_documentation.json`
- Sharing Guide: `docs/SHARE_WITH_WEBSITE.md`
- Original Files: `backup_before_clean/`

---

**Clean, organized, and ready for production!** 🎉

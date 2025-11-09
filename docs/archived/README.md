# Archived docs/README.md

This file is an archived copy of the previous `docs/README.md` that described the project layout and quick start.

Location of active documentation:
- Root `README.md` — the current, canonical README for developers.

If you need the original full docs text, it is preserved here.

---

# LLM Document Processing System (archived)

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
│   ├── README.md          # This file (archived)
│   └── SHARE_WITH_WEBSITE.md # Webhook sharing guide
├── data/                  # Insurance policy documents
│   └── *.pdf             # 6 real insurance policies
├── config/                # Configuration files
│   └── .env.example      # Environment template
└── backup_before_clean/   # Backup of original files
```

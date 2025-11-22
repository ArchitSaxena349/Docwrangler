# 🏥 LLM DocWrangler — Insurance Document Processing


Comprehensive, practical README for developers and contributors. This project extracts, indexes, and answers
questions about insurance documents using local embeddings and Google's Gemini API. It's intended as a
developer-friendly reference implementation and evaluation harness.

Contents
- What this repo does
- Quick start (venv)
- Project layout and key files
- Running the example scripts and webhook
- Data and vector store handling
- Environment variables and secrets
- Troubleshooting & notes
- Contributing

What this repo does
-------------------
- Extracts text from PDF insurance policies (see `data/`)
- Builds local embeddings (SentenceTransformers) and stores them in a ChromaDB vector store
- Exposes a minimal webhook API (`webhook/basic_webhook_server.py`) for demoing the service

Quick start (lightweight, PowerShell)
------------------------------------
This is the fastest way to run the example scripts locally. It installs a safe subset of packages and avoids heavy native builds.

1) Create and activate a venv (PowerShell):

```powershell
& "C:/Path/To/python.exe" -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

2) Upgrade packaging tools and install minimal runtime packages:

- `src/` — main application code (API, document processors, retrieval, services)
  - `src/api/` — webhook routing and API glue
  - `src/document_processor/` — PDF/Word/email processors
  - `src/retrieval/` — vector store wrapper (Chroma)
- `data/` — source PDFs and runtime generated stores
  - `data/vector_store/` — centralized location for Chroma DB files (ignored by Git)
- `webhook/` — simple demo webhook server

Key files you’ll use
- `webhook/basic_webhook_server.py` — minimal webhook to demonstrate endpoints and payloads
- `requirements.txt` — full pinned requirements (use with caution on Windows; prefer conda)

Vector store & data handling
---------------------------
- By default the project stores local Chroma vector DB files under `data/vector_store/local_chroma_db/`.
- This folder is ignored by Git via `.gitignore`.
- To reset the store, stop any running service and remove the folder:

```powershell
Remove-Item -Recurse -Force data\vector_store\local_chroma_db
```

Environment variables & secrets
-------------------------------
- Create a `.env` file at the project root or export environment variables in your shell.
- Supported variables:
  - `OPENAI_API_KEY` — (optional) enable OpenAI completions in the local embedding test

Troubleshooting & common notes
------------------------------
- Pandas / numpy on Windows: pinned `pandas==2.1.4` in `requirements.txt` expects `numpy<2,>=1.26` which often requires a compiler to build on Windows. Use conda/mamba to obtain binary wheels.
- If a package install fails while building native extensions, prefer creating a conda environment and installing from `conda-forge`.
- If the webhook health endpoint fails, make sure no other process is listening on the port (default 8001). You can change the port in `webhook/basic_webhook_server.py`.

Developer tips
--------------

Cleaning up
-----------
- Remove virtualenv and generated stores:

```powershell
Remove-Item -Recurse -Force .venv
Remove-Item -Recurse -Force data\vector_store\local_chroma_db
```

Contributing
------------
- Contributions are welcome. Please open issues for bugs or feature requests or create PRs with small, focused changes.

License
-------
This repository does not include a license file. Add `LICENSE` if you intend to open-source the project and choose a license.



## 📄 Example Usage

```bash
# Test insurance claim
curl -X POST http://localhost:8001/webhook/insurance-claim \
  -H "Content-Type: application/json" \
  -d '{
    "age": 46,
    "gender": "male",
    "procedure": "knee surgery",
    "policy_duration": "3 months",
    "claim_amount": 50000
  }'

# Response: {"decision": "approved", "coverage_amount": 50000, "confidence_score": 0.90}
```

## 📁 Project Structure

```
├── core/           # Configuration and models
├── webhook/        # Webhook server and API
├── data/          # Insurance policy PDFs
```

## 🎯 Ready For

- **Production deployment**
- **Integration with websites**
- **Real insurance claim processing**
- **API consumption by other applications**

---

**Clean, functional, and ready to use!** 🎉

# Developer Notes

These notes capture practical tips for working on this repo on Windows with PowerShell.

## Environments

- Quick start (built-in venv):
  - Create/activate: run `scripts/create_venv.ps1` (uses `$env:PYTHON_EXE` if set, else `python`).
  - Install minimal runtime deps as needed when running scripts (pip will be used on-demand).
- Recommended (for heavy scientific deps):
  - Use Conda/Mamba for prebuilt binaries (NumPy/Pandas/PyTorch/etc.).
  - We can generate an `environment.yml` on request.

## Helpful scripts

- `scripts/create_venv.ps1` — creates `.venv` and prints activation command.
- `scripts/run_tests.ps1` — runs the two local verification scripts.
- `scripts/run_webhook.ps1` — starts the demo webhook server.

## Data and vector store

- Local Chroma DB persists under `data/vector_store/local_chroma_db`.
- The path is centralized in `core/config.py` as `CHROMA_PERSIST_DIRECTORY`.

## Project structure highlights

- `core/` — central config (`Config`) and pydantic models used across modules.
- `src/` — services, retrieval, processors, and engines.
- `tests/` — example scripts that exercise PDF processing and embeddings.
- `webhook/` — demo server (HTML/JSON test artifacts moved to `archive/`).
- `archive/` — preserved demo/test assets not needed for runtime.

## Housekeeping

- Temporary files (`__pycache__`, `.pytest_cache`, `*.pyc`) are safe to delete.
- Keep `.venv/` and `data/vector_store/` — they are ignored by Git.

## Troubleshooting

- If pip install fails on Windows for native packages, prefer Conda/Mamba.
- If embeddings or vector DB path issues occur, check `core/config.py`.
- For OpenAI-dependent features, ensure the package and API key are configured; scripts fallback to local analysis if unavailable.# Development notes

This repository contains scripts to process insurance PDFs and run local embedding-based analysis.

Quick setup (PowerShell, Windows)

1. Create a lightweight virtual environment and install minimal packages (recommended for quick runs):

```powershell
& "C:/Path/To/python.exe" -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
& .\.venv\Scripts\python.exe -m pip install pytest pypdf2 chromadb sentence-transformers
```

2. Run the example scripts:

```powershell
& .\.venv\Scripts\python.exe tests/local_embedding_test.py
& .\.venv\Scripts\python.exe tests/offline_pdf_analyzer.py
```

Full environment (recommended for reproducible installs)

- Use conda/miniconda and install from conda-forge. This is the most reliable way to get binary wheels for numpy, pandas and torch on Windows.

Example (using conda/mamba):

```powershell
conda create -n llm_docwrangler python=3.11 -y
conda activate llm_docwrangler
mamba install -c conda-forge python=3.11 numpy=1.26 pandas=2.1.4 pytorch -y
pip install -r core/requirements.txt
```

Notes
- If you plan to use OpenAI, set `OPENAI_API_KEY` in `.env` or environment before running tests that call OpenAI.
- For large installs and ML dependencies prefer conda to avoid native build failures.

#!/usr/bin/env pwsh
<#
Activate the venv and run the project's two main test scripts.
#>

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtualenv not found. Run scripts/create_venv.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\python.exe tests/local_embedding_test.py
& .\.venv\Scripts\python.exe tests/offline_pdf_analyzer.py

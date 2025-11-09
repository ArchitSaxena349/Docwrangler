#!/usr/bin/env pwsh
<#
Create a .venv and install a minimal set of packages to run local tests.
This installs a minimal, safe subset to avoid heavy native builds.
#>

 # Prefer an explicitly set PYTHON_EXE environment variable, else use python from PATH
$python = $env:PYTHON_EXE
if (-not $python) {
    $python = "python"
}

& $python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
# Minimal safe installs for running tests (may still be heavy)
& .\.venv\Scripts\python.exe -m pip install pytest pypdf2 chromadb sentence-transformers -q

Write-Host "Virtualenv .venv created. Activate with: .\\.venv\\Scripts\\Activate.ps1" -ForegroundColor Green

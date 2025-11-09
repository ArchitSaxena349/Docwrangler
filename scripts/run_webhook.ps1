# Starts the demo webhook server using the repo's Python
param()

$python = $env:PYTHON_EXE
if (-not $python) { $python = "python" }

Write-Host "Starting webhook server..." -ForegroundColor Cyan
& $python "webhook/basic_webhook_server.py"

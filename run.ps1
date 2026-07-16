$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Creating venv..."
    python -m venv venv
    & venv\Scripts\pip install -r requirements.txt
}

Write-Host "Starting Cubism Chat..."
& venv\Scripts\python main.py

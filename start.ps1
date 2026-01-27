#!/usr/bin/env pwsh
# Activate the project venv and run Django dev server
if (Test-Path -Path .venv\Scripts\Activate.ps1) {
    . .\venv\Scripts\Activate.ps1
} else {
    Write-Host "No .venv found. Creating one..."
    py -3 -m venv .venv
    . .\venv\Scripts\Activate.ps1
    .venv\Scripts\python.exe -m pip install -r requirements.txt
}
python manage.py runserver

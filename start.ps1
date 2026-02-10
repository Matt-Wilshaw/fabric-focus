#!/usr/bin/env pwsh
# Activate the project venv and run Django dev server

$venvDir = if (Test-Path -Path ".\.venv\Scripts\python.exe") {
    ".venv"
} elseif (Test-Path -Path ".\venv\Scripts\python.exe") {
    "venv"
} else {
    $null
}

if (-not $venvDir) {
    Write-Host "No venv found (.venv/ or venv/). Creating .venv..."
    py -3 -m venv .venv
    $venvDir = ".venv"
}

$pythonExe = Join-Path $venvDir "Scripts\python.exe"
$activateScript = Join-Path $venvDir "Scripts\Activate.ps1"

if (Test-Path -Path $activateScript) {
    try {
        . $activateScript
    } catch {
        # If activation fails (e.g. execution policy), we still can run via python.exe directly.
    }
}

& $pythonExe -m pip install -r requirements.txt
& $pythonExe manage.py runserver

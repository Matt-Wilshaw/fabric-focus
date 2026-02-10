# Development: start the server

Use the project virtual environment in the repo root. This repo may have either `venv/` or `.venv/` (both are supported by the wrappers).

PowerShell (recommended):
```powershell
.\start.ps1
```

Command Prompt:
```cmd
run.bat
```

These wrappers will create the `.venv` (once), install `requirements.txt` into it, and run `manage.py runserver` using the venv's Python. This avoids reinstalling requirements for different interpreters.

If you want `python` to always work system-wide, add your system Python to PATH or enable the App Execution Alias for `python` in Windows Settings.

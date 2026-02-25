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

Local environment / secrets
- Store development-only secrets in `env.py` (this repo ignores `env.py`).
- Example (do NOT commit real keys):
```python
# env.py (local only)
os.environ.setdefault('STRIPE_PUBLIC_KEY', 'pk_test_...')
os.environ.setdefault('STRIPE_SECRET_KEY', 'sk_test_...')
```
- For CI / pipelines, set secrets via the pipeline environment variables instead of committing them.

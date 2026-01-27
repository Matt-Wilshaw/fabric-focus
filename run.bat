@echo off
if exist .venv\Scripts\activate.bat (
  .venv\Scripts\activate.bat
) else (
  py -3 -m venv .venv
  .venv\Scripts\activate.bat
  .venv\Scripts\python.exe -m pip install -r requirements.txt
)
python manage.py runserver

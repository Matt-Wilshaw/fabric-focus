@echo off

set "VENV_DIR="
if exist .venv\Scripts\python.exe set "VENV_DIR=.venv"
if not defined VENV_DIR if exist venv\Scripts\python.exe set "VENV_DIR=venv"

if not defined VENV_DIR (
  echo No venv found (.venv/ or venv/). Creating .venv...
  py -3 -m venv .venv
  set "VENV_DIR=.venv"
)

if exist %VENV_DIR%\Scripts\activate.bat call %VENV_DIR%\Scripts\activate.bat
%VENV_DIR%\Scripts\python.exe -m pip install -r requirements.txt
%VENV_DIR%\Scripts\python.exe manage.py runserver

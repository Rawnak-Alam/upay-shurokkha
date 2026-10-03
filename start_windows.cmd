@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Run setup_windows.cmd first.
 pause
 exit /b 1
)
.venv\Scripts\python.exe -m streamlit run app.py
pause

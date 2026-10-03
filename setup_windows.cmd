@echo off
cd /d "%~dp0"
py -3.12 --version >nul 2>&1
if errorlevel 1 (
  python -m venv .venv
) else (
  py -3.12 -m venv .venv
)
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 goto fail
echo Setup complete. Run start_windows.cmd next.
pause
exit /b 0
:fail
echo Setup failed. Copy the error above and ask for help. Python 3.12 is recommended.
pause
exit /b 1

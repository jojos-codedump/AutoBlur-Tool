@echo off
set "VENV_DIR=venv"
set "HOST=127.0.0.1"
set "PORT=8000"

echo [INFO] Starting AutoBlur Dashboard...

:: 1. Check if Virtual Environment exists
if not exist "%VENV_DIR%" (
    echo [ERROR] Virtual environment not found. 
    echo [HINT] Please run 'setup.cmd' first to install dependencies.
    pause
    exit /b
)

:: 2. Activate Virtual Environment
call "%VENV_DIR%\Scripts\activate.bat"

:: 3. Open Browser (Wait 2 seconds to ensure server starts)
echo [INFO] Opening browser...
timeout /t 2 /nobreak >nul
start http://%HOST%:%PORT%

:: 4. Start FastAPI Server
echo [INFO] Starting Backend Server...
echo [INFO] Press Ctrl+C to stop the server.
uvicorn app.main:app --reload --host %HOST% --port %PORT%

pause
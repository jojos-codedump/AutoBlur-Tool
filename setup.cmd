@echo off
setlocal EnableDelayedExpansion

echo ===================================================
echo      AutoBlur Tool - Clean Golden Setup
echo ===================================================

:: 1. Nuclear Cleanup: Remove previous broken environments
if exist "venv" (
    echo [INFO] Removing existing virtual environment...
    rd /s /q venv
)

:: 2. Cache Cleanup: Remove broken/experimental model caches
echo [INFO] Clearing Paddle cache folders...
if exist "%USERPROFILE%\.paddleocr" rd /s /q "%USERPROFILE%\.paddleocr"
if exist "%USERPROFILE%\.paddlex" rd /s /q "%USERPROFILE%\.paddlex"

:: 3. Create Fresh Virtual Environment
echo [INFO] Creating fresh virtual environment...
python -m venv venv
if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to create venv. Make sure Python is in your PATH.
    pause
    exit /b 1
)

:: 4. Activate and Upgrade Pip
call venv\Scripts\activate.bat
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

:: 5. Install Golden Stack Dependencies
:: We install directly from the requirements.txt to ensure the order is respected.
echo [INFO] Installing the Golden Stack (This may take several minutes)...
pip install -r requirements.txt --no-cache-dir

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Installation failed. Check your internet connection.
    pause
    exit /b 1
)

:: 6. Verify Installation
echo.
echo [INFO] Verifying core libraries...
python -c "import paddle; import paddleocr; print('SUCCESS: Paddle ' + paddle.__version__ + ' and OCR ' + paddleocr.__version__ + ' installed.')"

echo.
echo ===================================================
echo [SUCCESS] Golden Stack is ready!
echo Please ask me for the updated core.py now.
echo ===================================================
pause
@echo off
setlocal EnableDelayedExpansion

echo ===================================================
echo      AutoBlur Tool - Universal Setup Wizard
echo ===================================================

:: 1. Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.10 and add to PATH.
    pause
    exit /b 1
)

:: 2. Cleanup old attempts
if exist "venv" (
    echo [INFO] Removing old environment to ensure a clean slate...
    rd /s /q venv
)

:: 3. Create Fresh Virtual Environment
echo [INFO] Creating virtual environment...
python -m venv venv
if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b 1
)

:: 4. Activate & Bootstrap Build Tools
:: We use the absolute path to bypass PowerShell execution policy issues
call venv\Scripts\activate.bat

echo [INFO] Updating core build tools...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir

:: 5. Install the Golden Stack
:: We install NumPy FIRST to set the ABI standard for subsequent packages
echo [INFO] Installing stable math libraries...
pip install "numpy>=1.23.0,<1.24.0" --no-cache-dir

echo [INFO] Installing AI and Web dependencies (This takes 2-5 minutes)...
pip install -r requirements.txt --no-cache-dir

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Installation failed. Check internet connection.
    pause
    exit /b 1
)

:: 6. Auto-Create Project Folders
if not exist "app\static\css" mkdir "app\static\css"
if not exist "app\static\js" mkdir "app\static\js"
if not exist "app\templates" mkdir "app\templates"

echo.
echo ===================================================
echo [SUCCESS] Setup Complete!
echo You can now run the tool using 'run.cmd'.
echo ===================================================
pause

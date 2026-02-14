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

:: 2. Nuclear Cleanup
if exist "venv" (
    echo [INFO] Cleaning old environment...
    rd /s /q venv
)

:: 3. Create Virtual Environment
echo [INFO] Creating fresh virtual environment...
python -m venv venv
if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b 1
)

:: 4. Activate
call venv\Scripts\activate.bat

:: 5. THE BOOTSTRAP FIX
:: This installs the tools needed to build the other packages
echo [INFO] Bootstrapping build tools...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir

:: 6. Install Golden Stack
echo [INFO] Installing dependencies (This may take several minutes)...
:: We install these one by one to ensure the build tools are used correctly
pip install numpy^>=1.23.0,^<1.24.0 --no-cache-dir
pip install -r requirements.txt --no-cache-dir

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Installation failed.
    pause
    exit /b 1
)

:: 7. Create Structure
if not exist "app\static\css" mkdir "app\static\css"
if not exist "app\static\js" mkdir "app\static\js"
if not exist "app\templates" mkdir "app\templates"

echo.
echo ===================================================
echo [SUCCESS] Setup Complete on this machine!
echo ===================================================
pause

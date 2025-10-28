@echo off
setlocal enabledelayedexpansion

echo ======================================
echo   Morai ZED Demo Environment Setup
echo ======================================

echo [STEP 1] Create virtual environment
py -3.12 -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b 1
)
call venv\Scripts\activate

echo [STEP 2] Install dependencies
python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt || echo [WARN] Some packages failed to install.
) else (
    echo [WARN] requirements.txt not found, skipping.
)

echo [STEP 3] Searching for ZED SDK...

set "ZED_PATH="

for /d %%i in ("C:\Program Files\ZED SDK*") do set "ZED_PATH=%%i"
for /d %%i in ("C:\Program Files (x86)\ZED SDK*") do set "ZED_PATH=%%i"

if "%ZED_PATH%"=="" (
    echo [WARN] ZED SDK not found automatically.
    set /p ZED_PATH="Please input ZED SDK path manually (e.g., C:\Program Files (x86)\ZED SDK): "
) else (
    echo [INFO] Found ZED SDK at: !ZED_PATH!
)

if exist "!ZED_PATH!\get_python_api.py" (
    echo [STEP 4] Installing ZED Python API...
    python "!ZED_PATH!\get_python_api.py"
    if errorlevel 1 (
        echo [WARN] ZED Python API installation failed — continuing anyway.
    ) else (
        echo [INFO] ZED Python API installation complete.
    )
) else (
    echo [ERROR] get_python_api.py not found in !ZED_PATH!
    echo Please verify your ZED SDK installation.
)

echo.
echo [DONE] Environment setup complete!
pause

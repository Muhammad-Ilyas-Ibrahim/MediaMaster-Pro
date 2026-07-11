@echo off
REM Build script for Multi-Media-Master-Pro GUI v2.0
REM This script builds the executable with icon.ico using PyInstaller

echo ========================================
echo Multi-Media-Master-Pro Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.6 or higher and try again.
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

REM Check if PyInstaller is installed
echo [2/4] Checking PyInstaller installation...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully!
) else (
    echo PyInstaller is already installed.
)
echo.

REM Check if icon.ico exists
echo [3/4] Checking for icon.ico...
if not exist "icon.ico" (
    echo WARNING: icon.ico not found in current directory!
    echo The executable will be built without a custom icon.
    set ICON_ARG=
) else (
    echo icon.ico found!
    set ICON_ARG=--icon=icon.ico
)
echo.

REM Build the executable
echo [4/4] Building executable...
echo This may take a few minutes...
echo.

python -m PyInstaller ^
    --name=MultiMediaMasterPro ^
    --onedir ^
    --console ^
    %ICON_ARG% ^
    --add-data "ffmpeg.exe;." ^
    MultiMediaMasterPro_CLI.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The executable can be found in the 'dist' folder:
echo   dist\MultiMediaMasterPro.exe
echo.
echo IMPORTANT: Make sure to copy ffmpeg.exe to the same folder
echo            as the executable for the application to work!
echo.
pause


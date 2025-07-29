@echo off
REM Collection Import Tool for Windows
REM This batch file makes it easier to run the import tool on Windows

echo =================================================
echo Texture Reference Vault - Collection Import Tool
echo =================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Show usage if no arguments
if "%1"=="" (
    echo Usage: import_collection.bat [options]
    echo.
    echo Examples:
    echo   import_collection.bat --list-users
    echo   import_collection.bat --folder "C:\textures\wood" --name "Wood Pack" --owner admin_1
    echo.
    echo For full help:
    python import_collection.py --help
    pause
    exit /b 0
)

REM Run the Python script with all arguments
python import_collection.py %*

REM Pause to see results
if errorlevel 1 (
    echo.
    echo Import failed! Check the error messages above.
) else (
    echo.
    echo Import completed!
)
pause

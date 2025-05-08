@echo off
setlocal enabledelayedexpansion

:: Clear screen
cls
echo Installing dependencies...

:: Check for venv existence
if not exist ".venv\Scripts\pip.exe" (
    echo Virtual environment not found.
    set /p choice=Would you like to create one now? (y/n):
    if /i "!choice!"=="y" (
        echo Creating virtual environment in .venv...
        python -m venv .venv
    ) else (
        echo Aborting setup. Please create the virtual environment manually.
        exit /b 1
    )
)

:: Install dependencies
echo Installing dependencies...
.venv\Scripts\pip.exe install --disable-pip-version-check -r requirements.txt >nul 2>&1

echo Successfully installed, you can run by using run.bat

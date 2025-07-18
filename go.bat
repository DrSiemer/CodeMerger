@echo off

REM --- Configuration ---
set VENV_DIR=cc-venv
set START_SCRIPT=src.codemerger
set SPEC_FILE=codemerger.spec
set FLAG=%1

REM --- Environment Setup ---
REM Check if the virtual environment is already active
if "%VIRTUAL_ENV%"=="" (
    REM Check if the virtual environment directory exists
    if not exist "%VENV_DIR%\Scripts\activate" (
        echo Virtual environment not found. Creating a new one...
        python -m venv %VENV_DIR%

        REM Activate the virtual environment
        call %VENV_DIR%\Scripts\activate

        REM Install required packages from requirements.txt
        if exist requirements.txt (
            echo Installing required packages...
            pip install -r requirements.txt
        ) else (
            echo requirements.txt not found. Skipping package installation.
        )
    ) else (
        REM Activate the virtual environment if it already exists
        echo Activating virtual environment...
        call %VENV_DIR%\Scripts\activate
    )
)

REM --- Command Handling ---
REM Check for the 'build' flag (case-insensitive)
if /I "%FLAG%"=="b" (
    echo.
    echo --- Starting PyInstaller Build ---
    echo Deleting old build folders...
    rmdir /s /q dist
    rmdir /s /q build
    echo Running PyInstaller with %SPEC_FILE%...
    pyinstaller %SPEC_FILE%
    echo.
    echo --- Build Complete! ---
    echo Executable is located in the 'dist' folder.
    exit /b
)

REM Check for the 'cmd' flag to just open a command prompt
if /I "%FLAG%"=="cmd" (
    echo Virtual environment activated. You are now in a new command prompt.
    cmd /k
    exit /b
)

REM --- Default Action: Run the Python Script ---
echo Starting CodeMerger application...
python -m %START_SCRIPT%
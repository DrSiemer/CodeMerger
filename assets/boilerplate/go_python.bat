@echo off
setlocal enabledelayedexpansion

:: =================================================================
:: SECTION 1: CONFIGURATION
:: =================================================================
set "PROJECT_NAME=MyPythonApp"
set "VENV_DIR=.venv"
set "START_SCRIPT=src.main"
set "SPEC_FILE=%PROJECT_NAME%.spec"
set "VERSION_FILE=version.txt"
set "FLAG=%1"
set "ARG2=%2"

:: =================================================================
:: SECTION 2: COMMAND ROUTER
:: =================================================================
if /I "%FLAG%"=="" goto :DefaultAction
if /I "%FLAG%"=="cmd" goto :OpenCmd
if /I "%FLAG%"=="f" goto :FreezeReqs
if /I "%FLAG%"=="b" goto :BuildApp
if /I "%FLAG%"=="r" goto :HandleRelease
echo Unrecognized command: "%FLAG%".
goto :Usage

:DefaultAction
    call :ActivateVenv
    if !errorlevel! neq 0 goto :eof
    echo Starting %PROJECT_NAME%...
    python -m %START_SCRIPT%
    goto :eof

:OpenCmd
    call :ActivateVenv
    if !errorlevel! neq 0 goto :eof
    echo Virtual environment activated in new command prompt.
    cmd /k
    goto :eof

:FreezeReqs
    call :ActivateVenv
    if !errorlevel! neq 0 goto :eof
    echo Freezing dependencies to requirements.txt...
    pip freeze > requirements.txt
    echo Done.
    goto :eof

:BuildApp
    call :ActivateVenv
    if !errorlevel! neq 0 goto :eof
    echo.
    echo ### Starting Build Process ###
    echo.

    if /I "%ARG2%"=="cpu" (
        echo Forcing CPU-only PyTorch installation...
        pip install --force-reinstall torch torchaudio
    )

    echo Deleting old build folders...
    rmdir /s /q dist 2>nul
    rmdir /s /q build 2>nul
    echo.
    echo Running PyInstaller...
    pyinstaller %SPEC_FILE%
    if !errorlevel! neq 0 (
        echo.
        echo FATAL: PyInstaller build failed.
        goto :eof
    )
    echo.
    echo Build complete. Executable is in the 'dist' folder.
    goto :eof

:HandleRelease
    if not exist "release.bat" (
        echo ERROR: release.bat script not found.
        goto :eof
    )
    call release.bat %VERSION_FILE%
    goto :eof

:ActivateVenv
    if defined VIRTUAL_ENV exit /b 0

    if not exist "%VENV_DIR%\Scripts\activate" (
        echo.
        echo Virtual environment not found. Running one-time setup...
        python -m venv %VENV_DIR%
        if !errorlevel! neq 0 (
            echo ERROR: Failed to create venv. Verify Python installation and PATH.
            exit /b 1
        )
        call %VENV_DIR%\Scripts\activate
        echo.
        echo --- Upgrading Core Packaging Tools ---
        python -m pip install --upgrade pip setuptools wheel
        if exist requirements.txt (
            echo.
            echo --- Installing Application Requirements ---
            pip install -r requirements.txt
            if !errorlevel! neq 0 exit /b 1
        )
        echo.
        echo --- Setup complete! ---
        echo.
    ) else (
        call %VENV_DIR%\Scripts\activate
    )
    exit /b 0

:Usage
    echo.
    echo Commands:
    echo   (no flag) - Runs the main application script
    echo   cmd       - Opens a command prompt with the venv activated
    echo   f         - Freezes dependencies to requirements.txt
    echo   b         - Builds the application using PyInstaller
    echo   r         - Handles the release tagging process
    echo.
    goto :eof
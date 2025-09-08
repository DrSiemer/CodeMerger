@echo off
setlocal

REM Configuration
set VENV_DIR=cm-venv
set START_SCRIPT=src.codemerger
set SPEC_FILE=codemerger.spec
set FLAG=%1

REM Environment Setup
if "%VIRTUAL_ENV%"=="" (
    if not exist "%VENV_DIR%\Scripts\activate" (
        echo Virtual environment not found. Creating a new one...
        python -m venv %VENV_DIR%
        call %VENV_DIR%\Scripts\activate
        if exist requirements.txt (
            echo Installing required packages...
            pip install -r requirements.txt
        )
    ) else (
        echo Activating virtual environment...
        call %VENV_DIR%\Scripts\activate
    )
)

REM Main Command Router
if /I "%FLAG%"=="" goto :DefaultAction
if /I "%FLAG%"=="cmd" goto :OpenCmd
if /I "%FLAG%"=="f" goto :FreezeReqs
if /I "%FLAG%"=="b" goto :BuildApp
if /I "%FLAG%"=="r" goto :HandleRelease
echo Unrecognized command: %FLAG%
goto :eof

:DefaultAction
    echo Starting CodeMerger application...
    python -m %START_SCRIPT%
    goto :eof

:OpenCmd
    echo Virtual environment activated. You are now in a new command prompt.
    cmd /k
    goto :eof

:FreezeReqs
    echo.
    echo Writing requirements.txt
    pip freeze > requirements.txt
    echo Done.
    goto :eof

:GetVersion
    if not exist "version.txt" (
        echo ERROR: version.txt not found.
        exit /b 1
    )
    set "MAJOR_VER="
    set "MINOR_VER="
    set "REVISION_VER="
    for /f "tokens=1,2 delims==" %%a in (version.txt) do (
        if /i "%%a"=="Major" set "MAJOR_VER=%%b"
        if /i "%%a"=="Minor" set "MINOR_VER=%%b"
        if /i "%%a"=="Revision" set "REVISION_VER=%%b"
    )
    if not defined MAJOR_VER ( echo ERROR: "Major" version not found in version.txt. & exit /b 1 )
    if not defined MINOR_VER ( echo ERROR: "Minor" version not found in version.txt. & exit /b 1 )
    if not defined REVISION_VER ( echo ERROR: "Revision" version not found in version.txt. & exit /b 1 )
    set "VERSION=%MAJOR_VER%.%MINOR_VER%.%REVISION_VER%"
    exit /b 0

:BuildApp
    setlocal enabledelayedexpansion
    echo.
    echo Starting Build Process
    echo Deleting old build folders...
    rmdir /s /q dist 2>nul
    rmdir /s /q build 2>nul
    rmdir /s /q dist-installer 2>nul
    echo Running PyInstaller with %SPEC_FILE%...
    pyinstaller %SPEC_FILE%
    if !errorlevel! neq 0 (
        echo.
        echo FATAL: PyInstaller build failed.
        endlocal
        goto :eof
    )

    REM --- Installer Creation ---
    call :GetVersion
    if !errorlevel! neq 0 ( endlocal & goto :eof )

    set "INNO_SETUP_PATH="
    if exist "%ProgramFiles(x86)%\Inno Setup 6\iscc.exe" set "INNO_SETUP_PATH=%ProgramFiles(x86)%\Inno Setup 6\iscc.exe"
    if not defined INNO_SETUP_PATH if exist "%ProgramFiles%\Inno Setup 6\iscc.exe" set "INNO_SETUP_PATH=%ProgramFiles%\Inno Setup 6\iscc.exe"

    if not defined INNO_SETUP_PATH (
        echo.
        echo WARNING: Inno Setup not found. Skipping installer creation.
        echo To build an installer, download and install Inno Setup from jrsoftware.org
    ) else (
        echo Compiling installer with Inno Setup for v!VERSION!...
        (echo #define MyAppVersion "v!VERSION!") > version.iss
        "!INNO_SETUP_PATH!" setup.iss
        del version.iss
    )
    REM --- End Installer Creation ---

    echo.
    echo Build Complete!
    echo Executable is located in the 'dist' folder.
    if defined INNO_SETUP_PATH echo Installer is located in the 'dist-installer' folder.
    endlocal
    goto :eof

:HandleRelease
    setlocal enabledelayedexpansion
    echo.
    echo Handling Release Tag

    REM Check if on master branch
    set "CURRENT_BRANCH="
    for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set "CURRENT_BRANCH=%%b"

    if not defined CURRENT_BRANCH (
        echo ERROR: Could not determine the current git branch.
        echo Make sure this is a valid git repository. Aborting.
        endlocal
        goto :eof
    )

    if /I not "!CURRENT_BRANCH!"=="master" (
        echo.
        echo WARNING: You are not on the 'master' branch.
        echo Current branch is '!CURRENT_BRANCH!'.
        echo Releases should only be made from the 'master' branch.
        echo.
        echo Aborting release process.
        endlocal
        goto :eof
    )

    REM Get version
    call :GetVersion
    if !errorlevel! neq 0 ( endlocal & goto :eof )

    set "VERSION_TAG=v!VERSION!"
    echo Found version tag: !VERSION_TAG!

    REM --- Forcefully clean up any existing tags with the same name ---
    echo Checking for existing tags to determine release comment...
    set "IS_RETRIGGER=0"
    REM Check if tag exists locally OR remotely to set the flag
    git rev-parse "!VERSION_TAG!" >nul 2>nul
    if %errorlevel% equ 0 set "IS_RETRIGGER=1"
    git ls-remote --tags origin refs/tags/!VERSION_TAG! | findstr "refs/tags/!VERSION_TAG!" > nul
    if %errorlevel% equ 0 set "IS_RETRIGGER=1"

    REM Now, unconditionally delete remote and local tags, ignoring errors
    echo Cleaning up old tags...
    git push origin --delete !VERSION_TAG! >nul 2>nul
    git tag -d !VERSION_TAG! >nul 2>nul
    echo Cleanup complete.

    REM Get optional release comment
    shift /1
    set "COMMENT="
    :ArgLoop
    if "%~1"=="" goto EndArgLoop
    if not defined COMMENT (
        set "COMMENT=%~1"
    ) else (
        set "COMMENT=!COMMENT! %~1"
    )
    shift /1
    goto ArgLoop
    :EndArgLoop

    REM Default comment if user did not provide one
    if not defined COMMENT (
        if "!IS_RETRIGGER!"=="1" (
            set "COMMENT=Re-triggering release build for !VERSION_TAG!"
        ) else (
            set "COMMENT=Initial release for !VERSION_TAG!"
        )
    )
    echo Release comment: !COMMENT!

    REM Create and push tag
    echo Creating annotated tag !VERSION_TAG!...
    git tag -a "!VERSION_TAG!" -m "!COMMENT!"
    if %errorlevel% neq 0 (
        echo FATAL: Failed to create tag. Aborting.
        endlocal
        goto :eof
    )

    echo Pushing new tag !VERSION_TAG! to origin...
    git push origin !VERSION_TAG!
    echo.
    echo Release Action Triggered!
    endlocal
    goto :eof
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

:BuildApp
    echo.
    echo Starting PyInstaller Build
    echo Deleting old build folders...
    rmdir /s /q dist 2>nul
    rmdir /s /q build 2>nul
    echo Running PyInstaller with %SPEC_FILE%...
    pyinstaller %SPEC_FILE%
    echo.
    echo Build Complete!
    echo Executable is located in the 'dist' folder.
    goto :eof

:HandleRelease
    setlocal enabledelayedexpansion
    echo.
    echo Handling Release Tag

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

    REM Get version
    if not exist "assets\version.txt" (
        echo ERROR: assets\version.txt not found.
        goto :eof
    )
    set "MAJOR_VER="
    set "MINOR_VER="
    set "REVISION_VER="
    for /f "tokens=1,2 delims==" %%a in (assets\version.txt) do (
        if /i "%%a"=="Major" set "MAJOR_VER=%%b"
        if /i "%%a"=="Minor" set "MINOR_VER=%%b"
        if /i "%%a"=="Revision" set "REVISION_VER=%%b"
    )
    if not defined MAJOR_VER ( echo ERROR: "Major" version not found in version.txt. & goto :eof )
    if not defined MINOR_VER ( echo ERROR: "Minor" version not found in version.txt. & goto :eof )
    if not defined REVISION_VER ( echo ERROR: "Revision" version not found in version.txt. & goto :eof )

    set "VERSION=!MAJOR_VER!.!MINOR_VER!.!REVISION_VER!"
    set "VERSION_TAG=v!VERSION!"
    echo Found version tag: !VERSION_TAG!

    REM Clean up existing tags
    set "IS_RETRIGGER=0"
    git ls-remote --tags origin refs/tags/!VERSION_TAG! | findstr "refs/tags/!VERSION_TAG!" > nul
    if %errorlevel% equ 0 (
        echo Deleting remote tag !VERSION_TAG!...
        git push origin --delete !VERSION_TAG!
        set "IS_RETRIGGER=1"
    )
    git rev-parse "!VERSION_TAG!" >nul 2>nul
    if %errorlevel% equ 0 (
        echo Deleting local tag !VERSION_TAG!...
        git tag -d !VERSION_TAG!
        set "IS_RETRIGGER=1"
    )

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
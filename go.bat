@echo off
setlocal

REM Configuration
set VENV_DIR=cm-venv
set START_SCRIPT=run_webview.py
set SPEC_FILE=codemerger.spec
set FLAG=%1

REM Environment Setup
if "%VIRTUAL_ENV%"=="" (
    if not exist "%VENV_DIR%\Scripts\activate" (
        echo Virtual environment not found. Creating a new one

        python -m venv %VENV_DIR%
        call %VENV_DIR%\Scripts\activate
        call %VENV_DIR%\Scripts\activate
        if exist requirements.txt (
            echo Installing required packages

            pip install -r requirements.txt
        )
    ) else (
        echo Activating virtual environment

        call %VENV_DIR%\Scripts\activate
    )
)

REM Main Command Router
if /I "%FLAG%"=="" goto :DefaultAction
if /I "%FLAG%"=="i" goto :InstallFrontend
if /I "%FLAG%"=="br" goto :BuildAndRun
if /I "%FLAG%"=="dev" goto :DevAction
if /I "%FLAG%"=="debug" goto :DebugAction
if /I "%FLAG%"=="api" goto :ApiAction
if /I "%FLAG%"=="fe" goto :FrontendAction
if /I "%FLAG%"=="cmd" goto :OpenCmd
if /I "%FLAG%"=="f" goto :FreezeReqs
if /I "%FLAG%"=="b" goto :BuildFull
if /I "%FLAG%"=="ba" goto :BuildAppOnly
if /I "%FLAG%"=="bi" goto :BuildInstallerOnly
if /I "%FLAG%"=="r" goto :HandleRelease
echo Unrecognized command: %FLAG%
goto :eof

:DefaultAction
    for /f "usebackq delims=" %%a in (`powershell -command "([DateTime]::Now).ToString('dddd, yyyy-MM-dd HH:mm:ss', [System.Globalization.CultureInfo]::GetCultureInfo('en-US'))"`) do set "LOGTIME=%%a"
    echo Starting CodeMerger - %LOGTIME%

    REM Check if production frontend is built
    set BUILD_REQUIRED=0
    if not exist "frontend\dist\index.html" set BUILD_REQUIRED=1
    if not exist "frontend\dist\assets" set BUILD_REQUIRED=1

    if "%BUILD_REQUIRED%"=="1" (
        echo Production frontend not found or incomplete. Building now

        call :BuildFrontend
    )

    REM Using the venv python explicitly for consistency with go dev
    "%VENV_DIR%\Scripts\python.exe" %START_SCRIPT%
    goto :eof

:DebugAction
    echo Starting CodeMerger in Production Debug Mode (DevTools enabled)


    REM Ensure frontend is built first
    if not exist "frontend\dist\index.html" (
        call :BuildFrontend
    )

    "%VENV_DIR%\Scripts\python.exe" %START_SCRIPT% --debug
    goto :eof

:InstallFrontend
    echo Installing node modules

    cd frontend
    call npm install
    cd ..
    goto :eof

:BuildAndRun
    echo Rebuilding production frontend

    call :BuildFrontend
    echo Starting app

    goto :DefaultAction

:DevAction
    echo Starting Frontend and API concurrently


    call npm run dev
    goto :eof

:ApiAction
    echo Starting CodeMerger API only (Connecting to localhost:5173)

    "%VENV_DIR%\Scripts\python.exe" %START_SCRIPT% --dev
    goto :eof

:FrontendAction
    echo Starting Vue Frontend Dev Server

    cd frontend
    call npm run dev
    cd ..
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
    if not defined MAJOR_VER (
        echo ERROR: "Major" version not found in version.txt.
        exit /b 1
    )
    if not defined MINOR_VER (
        echo ERROR: "Minor" version not found in version.txt.
        exit /b 1
    )
    if not defined REVISION_VER (
        echo ERROR: "Revision" version not found in version.txt.
        exit /b 1
    )
    set "VERSION=%MAJOR_VER%.%MINOR_VER%.%REVISION_VER%"
    exit /b 0

:BuildFrontend
    echo.
    echo ===================================
    echo Compiling Vue Frontend

    echo ===================================
    cd frontend
    if not exist "node_modules" (
        echo Installing frontend dependencies

        call npm install
    )
    call npm run build
    cd ..
    if %errorlevel% neq 0 (
        echo FATAL: Frontend compilation failed.
        exit /b 1
    )
    exit /b 0

:BuildFull
    REM Full build requires cleaning to ensure the installer is accurate
    rmdir /s /q dist 2>nul
    rmdir /s /q build 2>nul
    rmdir /s /q dist-installer 2>nul

    call :BuildFrontend
    if %errorlevel% neq 0 goto :eof

    call :RunPyInstaller
    if %errorlevel% neq 0 goto :eof

    call :BuildInstaller
    if %errorlevel% neq 0 (
        echo Installer build failed. Check Inno Setup logs.
    )

    echo.
    echo Full Build Finished.
    goto :eof

:BuildAppOnly
    call :BuildFrontend
    if %errorlevel% neq 0 goto :eof

    call :RunPyInstaller
    goto :eof

:RunPyInstaller
    setlocal
    echo.
    echo Starting PyInstaller Build Process
    echo Running PyInstaller with %SPEC_FILE%
    pyinstaller %SPEC_FILE%
    if %errorlevel% neq 0 (
        echo.
        echo FATAL: PyInstaller build failed.
        endlocal
        exit /b 1
    )

    echo.
    echo Cleaning up loose executables from dist root

    del /q dist\*.exe 2>nul

    echo Executable build complete! Found in 'dist\CodeMerger\' folder.
    endlocal
    exit /b 0

:BuildInstallerOnly
    call :BuildInstaller
    goto :eof

:BuildInstaller
    setlocal enabledelayedexpansion
    echo.
    echo Starting Installer Build Process

    if not exist "dist\CodeMerger" (
        echo ERROR: 'dist\CodeMerger' folder not found.
        echo Run 'go b' first to create the application executable.
        endlocal
        exit /b 1
    )

    echo Deleting old installer folder

    rmdir /s /q dist-installer 2>nul

    call :GetVersion
    if !errorlevel! neq 0 ( endlocal & goto :eof )

    set "INNO_SETUP_PATH="
    if exist "%ProgramFiles(x86)%\Inno Setup 6\iscc.exe" set "INNO_SETUP_PATH=%ProgramFiles(x86)%\Inno Setup 6\iscc.exe"
    if not defined INNO_SETUP_PATH if exist "%ProgramFiles%\Inno Setup 6\iscc.exe" set "INNO_SETUP_PATH=%ProgramFiles%\Inno Setup 6\iscc.exe"

    if not defined INNO_SETUP_PATH (
        echo.
        echo WARNING: Inno Setup not found. Skipping installer creation.
        endlocal
        exit /b 1
    )

    echo Compiling installer with Inno Setup for v!VERSION!

    "!INNO_SETUP_PATH!" setup.iss /dMyAppVersion="!VERSION!"

    if !errorlevel! neq 0 (
        echo FATAL: Inno Setup build failed.
        endlocal
        exit /b 1
    )

    echo.
    echo Installer Build Complete! Found in 'dist-installer' folder.
    endlocal
    goto :eof

:HandleRelease
    setlocal enabledelayedexpansion
    echo.
    echo Handling Release Tag

    set "CURRENT_BRANCH="
    for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set "CURRENT_BRANCH=%%b"

    if not defined CURRENT_BRANCH (
        echo ERROR: Could not determine current git branch.
        endlocal
        goto :eof
    )

    if /I not "!CURRENT_BRANCH!"=="master" (
        echo.
        echo WARNING: You are not on the 'master' branch.
        endlocal
        goto :eof
    )

    call :GetVersion
    if !errorlevel! neq 0 ( endlocal & goto :eof )

    set "VERSION_TAG=v!VERSION!"
    echo Found version tag: !VERSION_TAG!

    echo Checking for existing tags

    set "IS_RETRIGGER=0"
    git rev-parse "!VERSION_TAG!" >nul 2>nul
    if %errorlevel% equ 0 set "IS_RETRIGGER=1"
    git ls-remote --tags origin refs/tags/!VERSION_TAG! | findstr "refs/tags/!VERSION_TAG!" > nul
    if %errorlevel% equ 0 set "IS_RETRIGGER=1"

    echo Cleaning up old tags

    git push origin --delete !VERSION_TAG! >nul 2>nul
    git tag -d !VERSION_TAG! >nul 2>nul

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

    if not defined COMMENT (
        if "!IS_RETRIGGER!"=="1" (
            set "COMMENT=Re-triggering release build for !VERSION_TAG!"
        ) else (
            set "COMMENT=Initial release for !VERSION_TAG!"
        )
    )
    echo Release comment: !COMMENT!

    echo Creating annotated tag !VERSION_TAG!

    git tag -a "!VERSION_TAG!" -m "!COMMENT!"
    if %errorlevel% neq 0 (
        echo FATAL: Failed to create tag.
        endlocal
        goto :eof
    )

    echo Pushing new tag !VERSION_TAG! to origin

    git push origin !VERSION_TAG!
    echo Release Action Triggered.
    endlocal
    goto :eof
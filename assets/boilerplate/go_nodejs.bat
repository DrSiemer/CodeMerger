@echo off
setlocal

set "PROJECT_NAME=MyNodeProject"
set "FLAG=%1"

if "%FLAG%"=="" goto :DefaultAction
if /I "%FLAG%"=="i" goto :InstallDeps
if /I "%FLAG%"=="dev" goto :RunDev
if /I "%FLAG%"=="b" goto :RunBuild
if /I "%FLAG%"=="s" goto :RunStart
if /I "%FLAG%"=="x" goto :RunStop
if /I "%FLAG%"=="r" goto :HandleRelease
echo Unrecognized command: "%FLAG%"
goto :Usage

:DefaultAction
    echo Starting %PROJECT_NAME% in production mode...
    call :CheckNodeModules
    if errorlevel 1 goto :eof
    npm start
    goto :eof

:InstallDeps
    echo Installing node modules...
    npm install
    goto :eof

:RunDev
    echo Starting development server...
    call :CheckNodeModules
    if errorlevel 1 goto :eof
    npm run dev
    goto :eof

:RunBuild
    echo Creating a production build...
    call :CheckNodeModules
    if errorlevel 1 goto :eof
    npm run build
    goto :eof

:RunStart
    echo Starting production server via process manager (e.g., pm2)...
    call :CheckNodeModules
    if errorlevel 1 goto :eof
    npm start
    goto :eof

:RunStop
    echo Stopping server...
    npm run stop
    goto :eof

:HandleRelease
    if not exist "release.bat" (
        echo ERROR: release.bat script not found.
        goto :eof
    )
    call release.bat version.txt
    goto :eof

:CheckNodeModules
    if not exist "node_modules" (
        echo.
        echo WARNING: 'node_modules' folder not found.
        echo ACTION: Run 'go i' to install dependencies.
        echo.
        exit /b 1
    )
    exit /b 0

:Usage
    echo.
    echo Commands:
    echo   i    - Installs dependencies (npm install)
    echo   dev  - Starts the development server (npm run dev)
    echo   b    - Builds the application for production (npm run build)
    echo   s    - Starts the production application (npm start)
    echo   x    - Stops the production application (npm run stop)
    echo   r    - Handles the release tagging process
    goto :eof
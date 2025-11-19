@echo off
setlocal

set "PROJECT_NAME=my-docker-project"
set "FLAG=%1"

if "%FLAG%"=="" goto :StartEnv
if /I "%FLAG%"=="i" goto :InstallDeps
if /I "%FLAG%"=="u" goto :UpdateDeps
if /I "%FLAG%"=="x" goto :StopEnv
if /I "%FLAG%"=="shell" goto :OpenShell
if /I "%FLAG%"=="build" goto :BuildEnv
echo Unrecognized command: "%FLAG%".
goto :Usage

:StartEnv
    echo Starting Docker environment for '%PROJECT_NAME%'...
    docker-compose -p %PROJECT_NAME% up -d
    goto :eof

:StopEnv
    echo Stopping Docker environment for '%PROJECT_NAME%'...
    docker-compose -p %PROJECT_NAME% stop
    goto :eof

:BuildEnv
    echo Building/rebuilding Docker images for '%PROJECT_NAME%'...
    docker-compose -p %PROJECT_NAME% build
    goto :eof

:InstallDeps
    echo Installing dependencies inside the container...
    REM Example for a PHP/Composer project:
    docker-compose -p %PROJECT_NAME% exec web composer install
    REM Example for a Node.js project:
    REM docker-compose -p %PROJECT_NAME% exec web npm install
    goto :eof

:UpdateDeps
    echo Updating dependencies inside the container...
    REM Example for a PHP/Composer project:
    docker-compose -p %PROJECT_NAME% exec web composer update
    REM Example for a Node.js project:
    REM docker-compose -p %PROJECT_NAME% exec web npm update
    goto :eof

:OpenShell
    echo Opening shell in 'web' container...
    docker-compose -p %PROJECT_NAME% exec web bash
    goto :eof

:Usage
    echo.
    echo Commands:
    echo   (no flag) - Starts the docker environment (up -d)
    echo   build     - Builds/rebuilds docker images
    echo   i         - Installs dependencies inside the container
    echo   u         - Updates dependencies inside the container
    echo   shell     - Opens a shell in the main 'web' container
    echo   x         - Stops the docker environment
    goto :eof
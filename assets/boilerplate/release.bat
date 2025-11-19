@echo off
setlocal enabledelayedexpansion

:: =================================================================
:: Reusable Release Script
:: Handles version checking, branch validation, and git tagging.
::
:: USAGE: call release.bat [path_to_version_file]
:: =================================================================

set "VERSION_FILE=%1"
if not defined VERSION_FILE (
    echo ERROR: Path to version file not specified.
    exit /b 1
)

:: --- 1. Get Version ---
call :GetVersion "%VERSION_FILE%"
if !errorlevel! neq 0 (
    echo Aborting: version file error.
    exit /b 1
)
set "VERSION_TAG=v!VERSION!"
echo Version found: !VERSION_TAG!

:: --- 2. Check Git Status ---
git diff-index --quiet HEAD --
if !errorlevel! neq 0 (
    echo.
    echo ERROR: Uncommitted changes detected in the working directory.
    echo Commit or stash changes before creating a release tag.
    exit /b 1
)
echo ✓ Git working directory clean.

:: --- 3. Check Branch ---
set "CURRENT_BRANCH="
for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set "CURRENT_BRANCH=%%b"
if /I not "!CURRENT_BRANCH!"=="master" if /I not "!CURRENT_BRANCH!"=="main" (
    echo.
    echo WARNING: Current branch is '!CURRENT_BRANCH!', not 'main' or 'master'.
    echo Releases should originate from a primary branch.
    exit /b 1
)
echo ✓ On primary branch ('!CURRENT_BRANCH!').

:: --- 4. Handle Existing Tag ---
echo Checking for existing remote/local tag '!VERSION_TAG!'...
git rev-parse "!VERSION_TAG!" >nul 2>&1
if !errorlevel! equ 0 (
    echo Deleting existing local tag.
    git tag -d !VERSION_TAG!
)
git ls-remote --tags origin refs/tags/!VERSION_TAG! | findstr "refs/tags/!VERSION_TAG!" > nul
if !errorlevel! equ 0 (
    echo Deleting existing remote tag.
    git push origin --delete !VERSION_TAG! >nul 2>&1
)

:: --- 5. Create and Push New Tag ---
echo.
echo Creating new annotated tag !VERSION_TAG!...
git tag -a "!VERSION_TAG!" -m "Release !VERSION_TAG!"
if !errorlevel! neq 0 (
    echo FATAL: Tag creation failed.
    exit /b 1
)

echo Pushing tag to origin...
git push origin !VERSION_TAG!
if !errorlevel! neq 0 (
    echo FATAL: Tag push to origin failed.
    exit /b 1
)

echo.
echo ### Release !VERSION_TAG! tagged and pushed successfully. ###
goto :eof

:GetVersion
    if not exist "%~1" (
        echo ERROR: Version file not found: '%~1'.
        exit /b 1
    )
    set "MAJOR_VER=" & set "MINOR_VER=" & set "REVISION_VER="
    for /f "tokens=1,2 delims==" %%a in (%~1) do (
        if /i "%%a"=="Major" set "MAJOR_VER=%%b"
        if /i "%%a"=="Minor" set "MINOR_VER=%%b"
        if /i "%%a"=="Revision" set "REVISION_VER=%%b"
    )
    if not defined MAJOR_VER ( echo ERROR: 'Major' version key not found in %~1. & exit /b 1 )
    if not defined MINOR_VER ( echo ERROR: 'Minor' version key not found in %~1. & exit /b 1 )
    if not defined REVISION_VER ( echo ERROR: 'Revision' version key not found in %~1. & exit /b 1 )
    set "VERSION=%MAJOR_VER%.%MINOR_VER%.%REVISION_VER%"
    exit /b 0
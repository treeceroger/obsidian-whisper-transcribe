@echo off
echo ================================================
echo Voice Notes Transcription - Quick Installer
echo ================================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell not found
    echo Please run install.ps1 manually
    pause
    exit /b 1
)

REM Run PowerShell installer
echo Running PowerShell installer...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

pause

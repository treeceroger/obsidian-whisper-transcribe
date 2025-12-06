#Requires -Version 5.1
<#
.SYNOPSIS
    Voice Notes Transcription - Automated Installer
.DESCRIPTION
    Installs and configures the Voice Notes Transcription system for Obsidian
    - Sets up Python backend
    - Installs plugin to Obsidian vault
    - Verifies prerequisites
.NOTES
    Run this script from the Transcribe directory
#>

param(
    [string]$VaultPath = "",
    [switch]$SkipBackend = $false,
    [switch]$SkipPlugin = $false
)

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warn { Write-Host $args -ForegroundColor Yellow }
function Write-Err { Write-Host $args -ForegroundColor Red }
function Write-Step {
    Write-Host ""
    Write-Host "=== $args ===" -ForegroundColor Magenta
    Write-Host ""
}

# Banner
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   Voice Notes Transcription - Installer             " -ForegroundColor Cyan
Write-Host "   Automated setup for Obsidian + Ollama             " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"
$PluginDir = Join-Path $ScriptDir "plugin"

# Step 1: Check Prerequisites
Write-Step "Step 1: Checking Prerequisites"

# Check Python
Write-Info "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -ge 3 -and $minor -ge 8) {
            Write-Success "[OK] Python $major.$minor found"
        } else {
            Write-Err "[FAIL] Python 3.8+ required (found $major.$minor)"
            Write-Info "Download from: https://www.python.org/downloads/"
            exit 1
        }
    }
} catch {
    Write-Err "[FAIL] Python not found"
    Write-Info "Download from: https://www.python.org/downloads/"
    Write-Info "Make sure to check 'Add Python to PATH' during installation"
    exit 1
}

# Check Ollama
Write-Info "Checking Ollama installation..."
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    $ollamaData = $ollamaCheck.Content | ConvertFrom-Json
    Write-Success "[OK] Ollama is running on port 11434"

    # Check for whisper model
    $hasWhisper = $ollamaData.models | Where-Object { $_.name -like "*whisper*" }
    if ($hasWhisper) {
        Write-Success "[OK] Whisper model found: $($hasWhisper.name)"
    } else {
        Write-Warn "[WARN] Whisper model not found"
        Write-Info "Run: ollama pull dimavz/whisper-tiny"
    }
} catch {
    Write-Err "[FAIL] Cannot connect to Ollama on localhost:11434"
    Write-Info "Make sure Ollama is running"
    Write-Info "Download from: https://ollama.ai"
    exit 1
}

# Step 2: Setup Backend
if (-not $SkipBackend) {
    Write-Step "Step 2: Setting Up Python Backend"

    Set-Location $BackendDir

    # Create virtual environment
    Write-Info "Creating Python virtual environment..."
    if (Test-Path "venv") {
        Write-Warn "Virtual environment already exists, skipping..."
    } else {
        python -m venv venv
        Write-Success "[OK] Virtual environment created"
    }

    # Get venv python and pip paths
    $venvPython = Join-Path $BackendDir "venv\Scripts\python.exe"
    $venvPip = Join-Path $BackendDir "venv\Scripts\pip.exe"

    # Install dependencies
    Write-Info "Installing Python dependencies..."
    Write-Info "(This may take a minute...)"

    # Upgrade pip, setuptools, and wheel
    Write-Info "Upgrading pip..."
    & $venvPython -m pip install --quiet --upgrade pip setuptools wheel

    # Install requirements using ONLY pre-built binary wheels (no compilation)
    Write-Info "Installing packages (binary wheels only)..."
    & $venvPip install --only-binary :all: -r requirements.txt

    Write-Success "[OK] Python dependencies installed"

    # Test backend
    Write-Info "Testing backend setup..."
    $testPython = @"
import sys
try:
    import flask
    import requests
    import sounddevice
    import numpy
    print('OK')
except ImportError as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"@

    $testResult = & $venvPython -c $testPython
    if ($testResult -eq 'OK') {
        Write-Success "[OK] Backend dependencies verified"
    } else {
        Write-Err "[FAIL] Backend dependency check failed: $testResult"
        exit 1
    }

    Set-Location $ScriptDir
} else {
    Write-Info "Skipping backend setup (--SkipBackend specified)"
}

# Step 3: Install Plugin to Obsidian
if (-not $SkipPlugin) {
    Write-Step "Step 3: Installing Plugin to Obsidian"

    # Find or ask for vault path
    if (-not $VaultPath) {
        Write-Info "Searching for Obsidian vaults..."

        # Common vault locations
        $possibleVaults = @()
        $documentsPath = [Environment]::GetFolderPath("MyDocuments")
        $userPath = [Environment]::GetFolderPath("UserProfile")

        # Search common locations
        $searchPaths = @(
            $documentsPath,
            $userPath,
            (Join-Path $userPath "Obsidian"),
            (Join-Path $documentsPath "Obsidian")
        )

        foreach ($searchPath in $searchPaths) {
            if (Test-Path $searchPath) {
                Get-ChildItem -Path $searchPath -Directory -Recurse -Depth 2 -ErrorAction SilentlyContinue |
                    Where-Object { Test-Path (Join-Path $_.FullName ".obsidian") } |
                    ForEach-Object { $possibleVaults += $_.FullName }
            }
        }

        if ($possibleVaults.Count -gt 0) {
            Write-Info "Found Obsidian vault(s):"
            for ($i = 0; $i -lt $possibleVaults.Count; $i++) {
                Write-Host "  [$($i+1)] $($possibleVaults[$i])"
            }

            if ($possibleVaults.Count -eq 1) {
                $VaultPath = $possibleVaults[0]
                Write-Success "Using vault: $VaultPath"
            } else {
                $selection = Read-Host "Select vault number (1-$($possibleVaults.Count)) or press Enter to specify path manually"
                if ($selection -and $selection -match '^\d+$') {
                    $index = [int]$selection - 1
                    if ($index -ge 0 -and $index -lt $possibleVaults.Count) {
                        $VaultPath = $possibleVaults[$index]
                    }
                }
            }
        }

        if (-not $VaultPath) {
            Write-Info "Enter the full path to your Obsidian vault:"
            Write-Info "Example: C:\Users\YourName\Documents\MyVault"
            $VaultPath = Read-Host "Vault path"
        }
    }

    # Validate vault path
    if (-not (Test-Path $VaultPath)) {
        Write-Err "[FAIL] Vault path does not exist: $VaultPath"
        exit 1
    }

    $obsidianDir = Join-Path $VaultPath ".obsidian"
    if (-not (Test-Path $obsidianDir)) {
        Write-Err "[FAIL] Not a valid Obsidian vault (no .obsidian folder): $VaultPath"
        exit 1
    }

    Write-Success "[OK] Valid Obsidian vault found"

    # Create plugins directory
    $pluginsDir = Join-Path $obsidianDir "plugins"
    if (-not (Test-Path $pluginsDir)) {
        New-Item -ItemType Directory -Path $pluginsDir -Force | Out-Null
        Write-Info "Created plugins directory"
    }

    # Create plugin directory
    $targetPluginDir = Join-Path $pluginsDir "voice-notes-transcription"
    if (Test-Path $targetPluginDir) {
        Write-Warn "Plugin directory already exists, updating..."
        Remove-Item -Path $targetPluginDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $targetPluginDir -Force | Out-Null

    # Copy plugin files
    Write-Info "Copying plugin files..."
    Copy-Item (Join-Path $PluginDir "main.js") $targetPluginDir
    Copy-Item (Join-Path $PluginDir "manifest.json") $targetPluginDir
    Copy-Item (Join-Path $PluginDir "styles.css") $targetPluginDir

    Write-Success "[OK] Plugin files copied to: $targetPluginDir"
    Write-Info "Files installed:"
    Write-Info "  - main.js"
    Write-Info "  - manifest.json"
    Write-Info "  - styles.css"
} else {
    Write-Info "Skipping plugin installation (--SkipPlugin specified)"
}

# Step 4: Verify Installation
Write-Step "Step 4: Verifying Installation"

$allGood = $true

# Check backend files
if (Test-Path (Join-Path $BackendDir "venv")) {
    Write-Success "[OK] Backend virtual environment exists"
} else {
    Write-Warn "[WARN] Backend virtual environment not found"
    $allGood = $false
}

# Check plugin files
if ($VaultPath -and (Test-Path (Join-Path $targetPluginDir "main.js"))) {
    Write-Success "[OK] Plugin installed to vault"
} else {
    Write-Warn "[WARN] Plugin files not found in vault"
    $allGood = $false
}

# Final Summary
Write-Step "Installation Complete!"

if ($allGood) {
    Write-Success ""
    Write-Success "[OK] Everything is set up and ready to go!"
    Write-Success ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "======================================================="
    Write-Host ""
    Write-Host "1. START BACKEND SERVICE"
    Write-Host "   Run this command in a new terminal:"
    Write-Host ""
    Write-Host "   cd `"$BackendDir`""
    Write-Host "   .\start.bat"
    Write-Host ""
    Write-Host "2. OPEN OBSIDIAN"
    Write-Host "   - Launch Obsidian"
    Write-Host "   - Open vault: $VaultPath"
    Write-Host ""
    Write-Host "3. ENABLE PLUGIN"
    Write-Host "   - Settings -> Community Plugins"
    Write-Host "   - Turn OFF 'Restricted Mode' (if enabled)"
    Write-Host "   - Enable 'Voice Notes Transcription'"
    Write-Host ""
    Write-Host "4. TEST IT OUT!"
    Write-Host "   - Click the microphone icon in the left sidebar"
    Write-Host "   - Speak: 'This is my first voice note'"
    Write-Host "   - Click microphone again to stop"
    Write-Host "   - Open 'Voice Notes.md' to see your transcription!"
    Write-Host ""
    Write-Host "======================================================="
    Write-Host ""
    Write-Host "Start backend now? (Y/N)" -ForegroundColor Yellow

    $startNow = Read-Host
    if ($startNow -eq 'Y' -or $startNow -eq 'y') {
        Write-Info ""
        Write-Info "Starting backend service..."
        Start-Process cmd -ArgumentList "/k cd /d `"$BackendDir`" && start.bat"
        Write-Success "[OK] Backend service started in new window"
        Write-Info "Keep that window open while using voice notes!"
    } else {
        Write-Info ""
        Write-Info "Remember to start the backend later with:"
        Write-Info "  cd $BackendDir"
        Write-Info "  .\start.bat"
    }

} else {
    Write-Warn ""
    Write-Warn "[WARN] Installation completed with warnings."
    Write-Warn "Please review the messages above and fix any issues."
    Write-Warn ""
    Write-Warn "For help, see: INSTALL.md"
}

Write-Host ""

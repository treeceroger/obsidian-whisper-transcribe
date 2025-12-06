# Installation Guide

Complete step-by-step installation instructions for the Voice Notes Transcription system.

## System Requirements

- **Operating System**: Windows (primary), Mac/Linux (experimental)
- **Obsidian**: v0.15.0 or later
- **Python**: 3.8 or later
- **Node.js**: v16 or later (for building plugin)
- **Disk Space**: ~500MB (for dependencies and models)
- **RAM**: 2GB minimum, 4GB recommended

## Part 1: Install Prerequisites

### 1.1 Install Python

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ CHECK "Add Python to PATH"
4. Click "Install Now"

**Verify:**
```bash
python --version
# Should show: Python 3.8.x or higher
```

### 1.2 Install Node.js

**Windows:**
1. Download from https://nodejs.org/
2. Run installer
3. Use default options

**Verify:**
```bash
node --version
npm --version
```

### 1.3 Install Ollama

**Windows:**
1. Download from https://ollama.ai
2. Run installer
3. Ollama will start automatically

**Mac:**
```bash
brew install ollama
ollama serve
```

**Verify:**
```bash
ollama list
```

### 1.4 Download Whisper Model

```bash
ollama pull dimavz/whisper-tiny
```

**Verify:**
```bash
ollama list
# Should show: dimavz/whisper-tiny
```

## Part 2: Install Backend Service

### 2.1 Navigate to Backend

```bash
cd E:\Transcribe\backend
```

### 2.2 Run Installation Script

**Windows:**
```bash
start.bat
```

This will:
1. Create Python virtual environment
2. Install all dependencies
3. Start the service

**Manual Installation (if needed):**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python service.py
```

### 2.3 Verify Backend

Open browser to: http://localhost:8765/status

You should see:
```json
{
  "service": "running",
  "ollama_connected": true,
  "model_available": true,
  ...
}
```

**Keep this terminal open** - the backend needs to run while using the plugin.

## Part 3: Build Obsidian Plugin

### 3.1 Navigate to Plugin Directory

Open a **NEW** terminal/command prompt:

```bash
cd E:\Transcribe\plugin
```

### 3.2 Install Dependencies

```bash
npm install
```

This will download TypeScript, esbuild, and Obsidian types.

### 3.3 Build the Plugin

```bash
npm run build
```

This creates `main.js` - the compiled plugin file.

**Verify:**
```bash
dir main.js
# File should exist
```

## Part 4: Install Plugin to Obsidian

### 4.1 Locate Your Vault

Find your Obsidian vault folder. Usually:
- Windows: `C:\Users\<YourName>\Documents\MyVault`
- Mac: `/Users/<YourName>/Documents/MyVault`

### 4.2 Create Plugin Directory

Navigate to your vault and create:
```
<YourVault>/.obsidian/plugins/voice-notes-transcription/
```

**Windows Command:**
```bash
mkdir "%USERPROFILE%\Documents\MyVault\.obsidian\plugins\voice-notes-transcription"
```

### 4.3 Copy Plugin Files

Copy these 3 files from `E:\Transcribe\plugin\` to the plugin directory:
- `main.js`
- `manifest.json`
- `styles.css`

**Windows Command:**
```bash
copy E:\Transcribe\plugin\main.js "%USERPROFILE%\Documents\MyVault\.obsidian\plugins\voice-notes-transcription\"
copy E:\Transcribe\plugin\manifest.json "%USERPROFILE%\Documents\MyVault\.obsidian\plugins\voice-notes-transcription\"
copy E:\Transcribe\plugin\styles.css "%USERPROFILE%\Documents\MyVault\.obsidian\plugins\voice-notes-transcription\"
```

### 4.4 Enable Plugin in Obsidian

1. Open Obsidian
2. Open Settings (gear icon)
3. Go to **Community Plugins**
4. Turn OFF **Restricted Mode** (if enabled)
5. Click **"Browse"** or refresh the list
6. Find **"Voice Notes Transcription"**
7. Click the toggle to **ENABLE** it

You should see a microphone icon appear in the left ribbon!

## Part 5: Configure Plugin

### 5.1 Open Plugin Settings

1. Settings → Voice Notes Transcription
2. Review default settings:
   - Backend URL: `http://localhost:8765` ✓
   - Ollama URL: `http://localhost:11434` ✓
   - Model: `dimavz/whisper-tiny` ✓
   - Notes file: `Voice Notes.md` ✓

### 5.2 Test Connection

1. Click **"Test Connection"** button
2. Should show:
   - ✓ Backend service is running
   - ✓ Ollama is connected
   - ✓ Model is available

If any ✗ appears, see Troubleshooting below.

## Part 6: First Voice Note

### 6.1 Start Recording

Click the microphone icon in the left ribbon.

Status bar should show: **🔴 Recording...**

### 6.2 Speak Your Note

Speak clearly: "This is my first voice note test."

### 6.3 Stop Recording

Click the microphone icon again.

Status bar shows: **⏳ Processing...** then **✓ Transcribed**

### 6.4 Check Your Note

Open the file: `Voice Notes.md`

You should see:
```markdown
## [2024-12-06 15:30:45]
This is my first voice note test.

```

**🎉 Success! Your voice transcription system is working!**

## Troubleshooting

### Backend Connection Failed

**Symptoms:**
- ✗ Backend service is not responding
- Cannot connect to backend service

**Solutions:**
1. Make sure backend is running (check terminal)
2. Restart backend: Close terminal, run `start.bat` again
3. Check port 8765 is not in use: `netstat -ano | findstr :8765`
4. Try changing backend port in `service.py`

### Ollama Not Connected

**Symptoms:**
- ✗ Ollama is not connected

**Solutions:**
1. Check Ollama is running: Open Task Manager, look for "ollama"
2. Restart Ollama: Close and open Ollama app
3. Test manually: `curl http://localhost:11434/api/tags`
4. Reinstall Ollama if needed

### Model Not Available

**Symptoms:**
- ✗ Model not found

**Solutions:**
1. Pull model again: `ollama pull dimavz/whisper-tiny`
2. Verify: `ollama list` should show the model
3. Check spelling in settings (case-sensitive!)

### No Microphone / Audio Error

**Symptoms:**
- Backend shows audio device errors
- Recording fails immediately

**Solutions:**
1. Check microphone is plugged in
2. Windows: Settings → Privacy → Microphone → Allow apps
3. Test microphone in other apps first
4. List devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`

### Plugin Not Showing in Obsidian

**Symptoms:**
- Plugin not in Community Plugins list
- No microphone icon

**Solutions:**
1. Verify files are in correct location
2. Check all 3 files exist: `main.js`, `manifest.json`, `styles.css`
3. Restart Obsidian completely
4. Check Console (Ctrl+Shift+I) for errors
5. Re-copy files

### Build Failed (npm run build)

**Symptoms:**
- Errors during `npm run build`
- `main.js` not created

**Solutions:**
1. Delete `node_modules` folder
2. Run `npm install` again
3. Try `npm run build` again
4. Check Node.js version: `node --version` (should be v16+)

## Daily Use

### Starting the System

**Every time you want to use voice notes:**

1. **Start Backend** (if not running):
   ```bash
   cd E:\Transcribe\backend
   start.bat
   ```

2. **Open Obsidian** - plugin loads automatically

3. **Start recording** - click microphone or use command palette

### Stopping the System

- **Backend**: Close the terminal or press Ctrl+C
- **Obsidian**: Just close Obsidian normally

## Next Steps

- [ ] Try different voice commands and lengths
- [ ] Customize the output file name in settings
- [ ] Set up auto-start for backend (see Advanced Setup)
- [ ] Deploy to your second computer (see README.md)

## Advanced Setup (Optional)

### Auto-start Backend on Windows Startup

1. Create shortcut to `start.bat`
2. Press Win+R, type `shell:startup`
3. Place shortcut in Startup folder

### Development Mode (auto-rebuild plugin)

```bash
cd plugin
npm run dev
```

Leave this running while editing TypeScript files.

## Getting Help

If you encounter issues:

1. Check backend terminal for error messages
2. Check Obsidian Console (Ctrl+Shift+I)
3. Review logs in backend service
4. Test each component individually:
   - Ollama: `ollama list`
   - Backend: `curl http://localhost:8765/status`
   - Plugin: Check Obsidian settings

## Success Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js installed
- [ ] Ollama installed and running
- [ ] dimavz/whisper-tiny model downloaded
- [ ] Backend service running (port 8765)
- [ ] Plugin built (`main.js` exists)
- [ ] Plugin files copied to vault
- [ ] Plugin enabled in Obsidian
- [ ] Connection test passes
- [ ] First voice note recorded successfully

**All checked? You're ready to go! 🎤**

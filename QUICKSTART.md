# Quick Start Guide

Get up and running in 5 minutes with the automated installer!

## Prerequisites

You only need:
- ✅ **Python 3.8+** - [Download](https://www.python.org/downloads/)
- ❌ **Ollama** - NOT needed anymore! Uses faster-whisper instead 🎉
- ❌ **Node.js** - NOT needed anymore! Plugin is pre-compiled 🎉

## One-Step Installation

### Option 1: Double-Click Install (Easiest)

1. **Double-click** `install-simple.bat`
2. Follow the prompts
3. Done!

### Option 2: PowerShell Install (Recommended)

Open PowerShell in the `E:\Transcribe` folder and run:

```powershell
.\install.ps1
```

That's it! The installer will:
- ✓ Check Python installation
- ✓ Set up backend virtual environment
- ✓ Install Python dependencies (faster-whisper, Flask, etc.)
- ✓ Find your Obsidian vault automatically
- ✓ Copy plugin files
- ✓ Offer to start the backend service

## What the Installer Does

```
╔═══════════════════════════════════════════════╗
║  Step 1: Check Prerequisites                 ║
║    ✓ Python 3.8+                             ║
║    ✓ No Ollama needed!                       ║
╠═══════════════════════════════════════════════╣
║  Step 2: Setup Backend                       ║
║    ✓ Create Python virtual environment       ║
║    ✓ Install dependencies (faster-whisper)   ║
║    ✓ Verify installation                     ║
║    ⏳ Whisper model downloads on first use   ║
╠═══════════════════════════════════════════════╣
║  Step 3: Install Plugin                      ║
║    ✓ Detect Obsidian vault location         ║
║    ✓ Copy main.js (pre-compiled!)           ║
║    ✓ Copy manifest.json                      ║
║    ✓ Copy styles.css                         ║
╠═══════════════════════════════════════════════╣
║  Step 4: Start Backend (optional)            ║
║    ✓ Launch backend service                  ║
╚═══════════════════════════════════════════════╝
```

## After Installation

### 1. Enable Plugin in Obsidian

1. Open **Obsidian**
2. Go to **Settings** → **Community Plugins**
3. Turn **OFF** "Restricted Mode" (if enabled)
4. **Enable** "Voice Notes Transcription"
5. You'll see a **🎤 microphone icon** in the left sidebar!

### 2. Test Your First Voice Note

**Manual Recording Test:**
1. **Click** the microphone icon 🎤
2. **Speak**: "This is my first voice note test"
3. **Click** microphone again to stop
4. **Open** the file: `Voice Notes.md`

You should see:
```markdown
## [2024-12-06 15:30:45]
This is my first voice note test.

```

**Wake Word Test (Recommended):**
1. **Click** the ear icon 👂 to enable Listen Mode
2. **Say**: "Obsidian Note"
3. **Speak**: "This is a wake word test" (watch it appear in real-time!)
4. **Say**: "Obsidian Stop"
5. **Check** `Voice Notes.md` - your note is saved!

**🎉 Success!**

## Daily Use

**Start the backend:**
```powershell
cd E:\Transcribe\backend
.\start.bat
```

Keep the terminal window open while using voice notes.

**Using voice notes:**
- **Wake Word Mode (Best)**: Click 👂 icon, then say "Obsidian Note" / "Obsidian Stop"
- **Manual Mode**: Click 🎤 icon to start/stop recording
- **Command Palette**: (Ctrl+P) → "Toggle Listen Mode" or "Toggle Voice Recording"
- **Microphone Selection**: Settings → Voice Notes Transcription → Audio Device

## Troubleshooting

### Installer says "Python not found"

Install Python from https://www.python.org/downloads/

**Important:** Check "Add Python to PATH" during installation!

### Installer can't find Obsidian vault

The installer will prompt you to enter the path manually:
```
Example: C:\Users\YourName\Documents\MyVault
```

### Backend won't start

```powershell
cd E:\Transcribe\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python service.py
```

### Plugin not showing in Obsidian

1. Check files are in: `<vault>/.obsidian/plugins/voice-notes-transcription/`
2. Restart Obsidian
3. Settings → Community Plugins → Refresh

## Manual Installation (If Needed)

If the automated installer doesn't work, see [INSTALL.md](INSTALL.md) for manual steps.

## Advanced Options

### Install to specific vault

```powershell
.\install.ps1 -VaultPath "C:\Path\To\Your\Vault"
```

### Skip backend setup (already done)

```powershell
.\install.ps1 -SkipBackend
```

### Skip plugin install (only setup backend)

```powershell
.\install.ps1 -SkipPlugin
```

### Update plugin only

```powershell
.\install.ps1 -SkipBackend
```

## What's Installed

```
E:\Transcribe\
├── backend\
│   └── venv\              ← Python virtual environment
│
Your Obsidian Vault\
└── .obsidian\
    └── plugins\
        └── voice-notes-transcription\
            ├── main.js       ← Pre-compiled plugin (no build needed!)
            ├── manifest.json
            └── styles.css
```

## Next Steps

- Configure settings in Obsidian → Voice Notes Transcription
- Try different recording lengths
- Customize the output file name
- Read [README.md](README.md) for full documentation

## Need Help?

1. **Test backend**: Open `test_api.html` in your browser
2. Check [INSTALL.md](INSTALL.md) for detailed steps
3. Review [README.md](README.md) for troubleshooting
4. Check backend terminal for error messages
5. **Test microphones**: Run `backend\test_devices.py`

### Common Issues

**Wake word not detecting:**
- Speak clearly and close to microphone
- Check backend console to see what it's hearing
- Try upgrading model in `backend/service.py` line 275

**No microphone devices showing:**
- Click "Refresh Devices" button in plugin settings
- Check Windows microphone permissions
- Run `backend\test_devices.py` to verify

**First-time model download slow:**
- The small.en model is ~244MB - takes a few minutes
- Watch backend console for download progress
- Only happens once!

---

**No Ollama. No Node.js. No complex builds. Just Python and PowerShell!** 🚀

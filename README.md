# Voice Notes Transcription for Obsidian

A lightweight voice-activated note-taking system for Obsidian using local faster-whisper transcription.

## 🎯 Features

- **Voice-to-Text**: Speak your thoughts, get them transcribed instantly
- **Wake Word Detection**: Say "Obsidian Note" to start, "Obsidian Stop" to finish
- **Real-time Streaming**: See your words appear in Obsidian as you speak
- **Obsidian Integration**: Native plugin with UI controls
- **Local & Private**: 100% local processing using faster-whisper (no internet required)
- **Timestamped Notes**: Every entry includes automatic timestamps
- **Microphone Selection**: Choose from any available input device
- **Single File**: All voice notes organized in one markdown file
- **Lightweight**: Minimal dependencies, simple setup

## 📋 Prerequisites

Before installation, make sure you have:

1. **Obsidian** (desktop app, v0.15.0+)
2. **Python 3.8+**
3. ~~**Ollama**~~ **NOT NEEDED!** Uses faster-whisper instead
4. ~~**Node.js**~~ **NOT NEEDED!** Plugin is pre-compiled!

## 🚀 Quick Start (Automated Installer)

### One-Command Installation

```powershell
# From the Transcribe directory:
.\install.ps1
```

Or just **double-click** `install-simple.bat`!

The installer will:
- ✓ Check Python installation
- ✓ Set up Python backend (venv + dependencies)
- ✓ Download faster-whisper model (small.en by default)
- ✓ Auto-detect your Obsidian vault
- ✓ Copy pre-compiled plugin files
- ✓ Offer to start the backend

**That's it!** See [QUICKSTART.md](QUICKSTART.md) for details.

### Manual Installation (If Needed)

<details>
<summary>Click to expand manual steps</summary>

#### Step 1: Set Up Backend Service

```bash
cd backend
start.bat
```

#### Step 3: Install Plugin

Copy these files from `plugin/` to your vault:
```
<YOUR_VAULT>/.obsidian/plugins/voice-notes-transcription/
├── main.js          (pre-compiled, no Node.js needed!)
├── manifest.json
└── styles.css
```

#### Step 4: Enable in Obsidian

1. Open Obsidian
2. Settings → Community Plugins
3. Enable "Voice Notes Transcription"

</details>

## 📖 Usage

### Recording a Voice Note

**Option 1: Wake Word Detection (Recommended)**
1. Click the ear icon in the left sidebar to enable Listen Mode
2. Say **"Obsidian Note"** to start recording
3. Speak your note - you'll see your words appear in real-time!
4. Say **"Obsidian Stop"** to finish

**Option 2: Manual Recording (Ribbon Icon)**
1. Click the microphone icon in the left sidebar
2. Speak your note
3. Click again to stop and transcribe

**Option 3: Command Palette**
1. Press `Ctrl+P` (or `Cmd+P`)
2. Type "Toggle Voice Recording" or "Toggle Listen Mode"
3. Speak your note
4. Run command again to stop

### Status Indicators

Watch the status bar (bottom right):
- 🎤 **Ready** - Ready to record
- 👂 **Listening...** - Wake word mode active, waiting for "Obsidian Note"
- 🔴 **Recording** - Currently recording your voice
- ⏳ **Processing** - Transcribing audio
- ✓ **Transcribed** - Successfully saved to your notes

### Real-time Streaming

When using wake word detection, your transcription appears **as you speak**:
- Text is transcribed in ~3-second chunks
- Each chunk appears immediately in your note
- No waiting until you finish speaking!

### Output Format

All transcriptions are saved to `Voice Notes.md` (configurable):

```markdown
## [2024-12-06 14:30:45]
Your transcribed voice note appears here in real-time as you speak.

## [2024-12-06 14:35:22]
Another note with its own timestamp.
```

## ⚙️ Configuration

Access settings via: **Settings → Voice Notes Transcription**

- **Backend Service URL**: Default `http://localhost:8765`
- **Voice Notes File**: Default `Voice Notes.md`
- **Wake Phrase**: "Obsidian Note" (currently fixed)
- **Stop Phrase**: "Obsidian Stop" (currently fixed)
- **Microphone**: Select from any available input device
  - Includes all physical and virtual audio devices
  - Auto-restarts listening when changed
  - System Default option available

## 📁 Project Structure

```
Transcribe/
├── backend/                      # Python transcription service
│   ├── service.py               # Main Flask server
│   ├── whisper_client.py        # Faster-Whisper client
│   ├── wake_word_listener.py    # Wake word detection
│   ├── requirements.txt         # Python dependencies (no scipy!)
│   ├── start.bat                # Windows startup script
│   └── test_devices.py          # Audio device testing
│
├── plugin/                      # Obsidian plugin (pre-compiled!)
│   ├── main.js                  # Plugin code (no build needed)
│   ├── manifest.json            # Plugin manifest
│   └── styles.css               # UI styles
│
├── install.ps1                  # Automated installer
├── install-simple.bat           # One-click installer
├── test_api.html                # Backend API testing tool
└── README.md                    # This file
```

## 🔧 Troubleshooting

### Backend Won't Start

```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
cd backend
python -m venv venv
venv\Scripts\activate
pip install --only-binary :all: -r requirements.txt
```

### Whisper Model Not Loading

The faster-whisper model downloads automatically on first use. If you see errors:

```bash
# Test the whisper client
cd backend
venv\Scripts\python.exe whisper_client.py
```

First-time setup may take a few minutes to download the small.en model (~244MB).

### Microphone Not Working

1. **Open plugin settings** → Audio Device section
2. **Click "Refresh Devices"** to reload microphone list
3. **Select your microphone** from the dropdown
4. **Test with manual recording** first (microphone icon)
5. **Check browser console** (Ctrl+Shift+I) for errors

If no devices show:
```bash
# Test audio device detection
cd backend
venv\Scripts\python.exe test_devices.py
```

### Plugin Not Loading

1. Verify files are in correct location: `<vault>/.obsidian/plugins/voice-notes-transcription/`
2. Check you have: `main.js`, `manifest.json`, `styles.css`
3. Restart Obsidian
4. Check Console for errors (Ctrl+Shift+I)

### Wake Word Not Detecting

1. Upgrade to a better model in `backend/service.py` (line 275):
   ```python
   init_whisper(model_size="medium.en")  # Better accuracy
   ```
2. Speak clearly and close to the microphone
3. Use the correct phrases: **"Obsidian Note"** and **"Obsidian Stop"**
4. Check the backend console - you'll see what it hears

### No Transcription / Empty Results

1. **Test backend status**: Open `test_api.html` in browser
2. **Check backend is running**: Look for console window
3. **Verify microphone permissions** in Windows Settings
4. **Test API manually**:
   ```bash
   curl http://localhost:8765/status
   curl http://localhost:8765/audio-devices
   ```

## 🔄 Deployment to Second Computer

### Quick Deployment

1. **Copy project folder** to second computer
2. **Run installer**:
   ```bash
   .\install.ps1
   ```
   Or just double-click `install-simple.bat`!
3. **Start backend**:
   ```bash
   cd backend
   start.bat
   ```
4. Plugin will be auto-installed if Obsidian vault is detected
5. **Enable plugin** in Obsidian settings

The faster-whisper model will download automatically on first use (no Ollama needed!).

### Sync Setup (Optional)

If you want to keep the plugin synced:
- Use Git repository for version control
- Use Obsidian Sync or other vault sync for the plugin folder
- Keep backend service folder separate (install on each machine)

## 🚧 Future Enhancements

- [x] Wake word detection ("Obsidian Note" / "Obsidian Stop") ✅
- [x] Real-time streaming transcription ✅
- [x] Microphone selection ✅
- [ ] Customizable wake/stop phrases
- [ ] Voice activity detection (auto-stop on silence)
- [ ] Recording time display
- [ ] Audio level indicator
- [ ] Multiple output file support
- [ ] Custom timestamp formats
- [ ] GPU acceleration support

## 📝 Development

### Backend Development

```bash
cd backend
python service.py
```

### Plugin Development

The plugin is written in plain JavaScript (no build step needed).
Edit `plugin/main.js` directly and copy to your vault to test changes.

## 📄 License

MIT - Personal use

## 🤝 Contributing

This is a personal project, but feel free to fork and modify for your own use!

## ❓ FAQ

**Q: Does this work offline?**
A: Yes! Everything runs locally - no internet required after initial model download.

**Q: Do I need Ollama?**
A: No! The project previously used Ollama but now uses faster-whisper directly, which is more reliable and faster.

**Q: How accurate is the transcription?**
A: Using small.en model, accuracy is excellent for clear English speech. For even better accuracy, you can upgrade to medium.en or large model in `backend/service.py`.

**Q: Can I use a different Whisper model?**
A: Yes! Edit line 275 in `backend/service.py` and change to: `tiny`, `base.en`, `small.en`, `medium.en`, or `large`.

**Q: Do I need Node.js?**
A: No! The plugin is pre-compiled. Just Python for the backend.

**Q: Does it work on Mac/Linux?**
A: Yes, though `start.bat` and `install.ps1` are Windows-specific. On Mac/Linux, manually activate venv and run `python service.py`.

**Q: Can I change the wake words?**
A: Currently the wake phrases are fixed to "Obsidian Note" and "Obsidian Stop". Customization is planned for a future update.

**Q: Does it support other languages?**
A: Currently optimized for English. For other languages, change `language="en"` in `whisper_client.py` and use a non-English model.

**Q: Why does transcription appear in chunks?**
A: This is the real-time streaming feature! Audio is transcribed every 3 seconds so you can see your words appear as you speak.

**Q: Can I use a Bluetooth microphone?**
A: Yes! Any audio input device (USB, Bluetooth, virtual audio cable) can be selected in the plugin settings.

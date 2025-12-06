# Voice Notes Transcription for Obsidian

A lightweight voice-activated note-taking system for Obsidian using local Ollama Whisper transcription.

## 🎯 Features

- **Voice-to-Text**: Speak your thoughts, get them transcribed instantly
- **Obsidian Integration**: Native plugin with UI controls
- **Local & Private**: 100% local processing using Ollama
- **Timestamped Notes**: Every entry includes automatic timestamps
- **Single File**: All voice notes organized in one markdown file
- **Lightweight**: Minimal dependencies, simple setup

## 📋 Prerequisites

Before installation, make sure you have:

1. **Obsidian** (desktop app, v0.15.0+)
2. **Python 3.8+**
3. **Ollama** with the `dimavz/whisper-tiny` model
4. ~~**Node.js**~~ **NOT NEEDED!** Plugin is pre-compiled!

## 🚀 Quick Start (Automated Installer)

### One-Command Installation

```powershell
# From the Transcribe directory:
.\install.ps1
```

Or just **double-click** `install-simple.bat`!

The installer will:
- ✓ Check Python and Ollama
- ✓ Set up Python backend (venv + dependencies)
- ✓ Auto-detect your Obsidian vault
- ✓ Copy pre-compiled plugin files
- ✓ Offer to start the backend

**That's it!** See [QUICKSTART.md](QUICKSTART.md) for details.

### Manual Installation (If Needed)

<details>
<summary>Click to expand manual steps</summary>

#### Step 1: Ensure Ollama Model

```bash
ollama pull dimavz/whisper-tiny
```

#### Step 2: Set Up Backend Service

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

**Option 1: Ribbon Icon**
1. Click the microphone icon in the left sidebar
2. Speak your note
3. Click again to stop and transcribe

**Option 2: Command Palette**
1. Press `Ctrl+P` (or `Cmd+P`)
2. Type "Toggle Voice Recording"
3. Speak your note
4. Run command again to stop

### Status Indicators

Watch the status bar (bottom right):
- 🎤 **Ready** - Ready to record
- 🔴 **Recording** - Currently recording your voice
- ⏳ **Processing** - Sending to Ollama for transcription
- ✓ **Transcribed** - Successfully saved to your notes

### Output Format

All transcriptions are saved to `Voice Notes.md` (configurable):

```markdown
## [2024-12-06 14:30:45]
Your transcribed voice note appears here.

## [2024-12-06 14:35:22]
Another note with its own timestamp.
```

## ⚙️ Configuration

Access settings via: **Settings → Voice Notes Transcription**

- **Backend Service URL**: Default `http://localhost:8765`
- **Ollama URL**: Default `http://localhost:11434`
- **Model Name**: Default `dimavz/whisper-tiny`
- **Voice Notes File**: Default `Voice Notes.md`

## 📁 Project Structure

```
Transcribe/
├── backend/               # Python transcription service
│   ├── service.py        # Main Flask server
│   ├── ollama_client.py  # Ollama API client
│   ├── requirements.txt  # Python dependencies
│   ├── start.bat         # Windows startup script
│   └── README.md
│
├── plugin/               # Obsidian plugin
│   ├── src/
│   │   ├── main.ts       # Plugin entry point
│   │   ├── settings.ts   # Settings UI
│   │   └── backendClient.ts  # API client
│   ├── manifest.json     # Plugin manifest
│   ├── package.json      # Node dependencies
│   └── README.md
│
├── REQUIREMENTS.md       # Detailed requirements
└── README.md            # This file
```

## 🔧 Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version

# Verify virtual environment
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Ollama Connection Failed

```bash
# Check if Ollama is running
ollama list

# Verify model is installed
ollama pull dimavz/whisper-tiny

# Test Ollama API
curl http://localhost:11434/api/tags
```

### Plugin Not Loading

1. Verify files are in correct location: `<vault>/.obsidian/plugins/voice-notes-transcription/`
2. Check you have: `main.js`, `manifest.json`, `styles.css`
3. Restart Obsidian
4. Check Console for errors (Ctrl+Shift+I)

### No Transcription / Empty Results

1. Check backend is running: `http://localhost:8765/status`
2. Verify microphone permissions
3. Test backend manually:
   ```bash
   curl -X POST http://localhost:8765/start-recording
   # Speak for a few seconds
   curl -X POST http://localhost:8765/stop-recording
   ```

## 🔄 Deployment to Second Computer

### Quick Deployment

1. **Copy project folder** to second computer
2. **Install Ollama** and pull model:
   ```bash
   ollama pull dimavz/whisper-tiny
   ```
3. **Start backend**:
   ```bash
   cd backend
   start.bat
   ```
4. **Copy plugin** to Obsidian vault
5. **Enable plugin** in Obsidian settings

### Sync Setup (Optional)

If you want to keep the plugin synced:
- Use Git repository for version control
- Use Obsidian Sync or other vault sync for the plugin folder
- Keep backend service folder separate (install on each machine)

## 🚧 Future Enhancements

- [ ] Wake word detection ("computer start note")
- [ ] Voice activity detection (auto-stop on silence)
- [ ] Recording time display
- [ ] Audio level indicator
- [ ] Multiple output file support
- [ ] Custom timestamp formats

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
A: Yes! Everything runs locally - no internet required.

**Q: How accurate is the transcription?**
A: Using whisper-tiny, accuracy is good for clear speech. For better accuracy, you can use larger models like `whisper-small` or `whisper-base`.

**Q: Can I use a different Whisper model?**
A: Yes! Pull any Whisper model in Ollama and change the model name in settings.

**Q: Do I need Node.js?**
A: No! The plugin is pre-compiled. Just Python for the backend.

**Q: Does it work on Mac/Linux?**
A: Yes, though `start.bat` and `install.ps1` are Windows-specific. On Mac/Linux, manually activate venv and run `python service.py`.

**Q: Can I change the wake word?**
A: Wake word detection is planned for Phase 3. Currently using manual triggers only.

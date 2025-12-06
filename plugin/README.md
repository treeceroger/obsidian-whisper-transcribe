# Voice Notes Transcription - Obsidian Plugin

Obsidian plugin for voice-activated note transcription using local Ollama Whisper model.

## Features

- 🎤 Manual voice recording with button/command
- 📝 Automatic transcription using Ollama
- ⏰ Timestamped entries
- 📄 All notes in one file
- 🔒 100% local processing

## Prerequisites

1. **Obsidian** desktop app installed
2. **Backend service** running (see `../backend/README.md`)
3. **Ollama** with `dimavz/whisper-tiny` model

## Installation

### Automated (Recommended)

Run the installer from the root directory:
```powershell
cd ..
.\install.ps1
```

### Manual Installation

No build step needed! The plugin is pre-compiled.

Copy these 3 files to your Obsidian vault:

**From:** `E:\Transcribe\plugin\`
**To:** `<VAULT_PATH>/.obsidian/plugins/voice-notes-transcription/`

**Files:**
- `main.js` (pre-compiled, ready to use!)
- `manifest.json`
- `styles.css`

Then:
1. Restart Obsidian
2. Settings → Community Plugins → Enable "Voice Notes Transcription"

## Usage

### Start Backend Service

Before using the plugin, start the backend service:
```bash
cd ..\backend
start.bat
```

### Recording Voice Notes

**Method 1: Ribbon Icon**
- Click the microphone icon in the left ribbon
- Speak your note
- Click again to stop and transcribe

**Method 2: Command Palette**
- Press `Ctrl+P` (or `Cmd+P` on Mac)
- Type "voice" and select:
  - "Start Voice Recording"
  - "Stop Voice Recording"
  - "Toggle Voice Recording"

**Status Indicators:**
- 🎤 Ready - Ready to record
- 🔴 Recording - Currently recording
- ⏳ Processing - Transcribing audio
- ✓ Transcribed - Successfully saved

### Settings

Go to Settings → Voice Notes Transcription to configure:

- **Backend Service URL**: URL of Python backend (default: http://localhost:8765)
- **Ollama URL**: URL of Ollama instance (default: http://localhost:11434)
- **Ollama Model**: Model name (default: dimavz/whisper-tiny)
- **Voice Notes File**: Target file name (default: Voice Notes.md)
- **Test Connection**: Verify backend is running

## Output Format

Transcriptions are appended to your configured file with timestamps:

```markdown
## [2024-12-06 14:30:45]
Your transcribed text appears here.

## [2024-12-06 14:35:22]
Another voice note with a different timestamp.
```

## Development

The plugin is written in plain JavaScript (no build step).

To modify:
1. Edit `main.js` directly
2. Copy to your vault's plugin folder
3. Reload Obsidian (Ctrl+R) or restart

## Troubleshooting

### Plugin won't load
- Make sure `main.js`, `manifest.json`, and `styles.css` exist
- Check the Console (Ctrl+Shift+I) for errors
- Try disabling and re-enabling the plugin

### "Backend service not running"
- Start the backend: `cd ..\backend && start.bat`
- Check backend URL in settings
- Test connection in settings panel

### Recording doesn't work
- Verify microphone permissions
- Check backend service is running
- Look at backend console for errors

### No transcription / Empty result
- Verify Ollama is running: `ollama list`
- Check model is available: `ollama pull dimavz/whisper-tiny`
- Test Ollama connection in settings

## Future Features

- 🎯 Wake word detection ("computer start note")
- 🔊 Audio level indicator while recording
- 📊 Recording time display
- ⚙️ Custom audio device selection

## License

MIT

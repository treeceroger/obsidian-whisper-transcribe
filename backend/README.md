# Voice Transcription Backend Service

Lightweight Python service that handles audio recording and transcription using faster-whisper.

## Prerequisites

1. **Python 3.8+** installed
2. ~~**Ollama**~~ **NOT NEEDED!** Uses faster-whisper directly

## Installation

### Windows (Automatic)
```bash
# Just run the start script - it will create venv and install dependencies
start.bat
```

The first time you run it, the faster-whisper model will download automatically (~244MB for small.en).

### Manual Installation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (binary wheels only, no compilation)
pip install --only-binary :all: -r requirements.txt
```

## Running the Service

### Windows
```bash
start.bat
```

### Mac/Linux
```bash
source venv/bin/activate
python service.py
```

The service will start on `http://localhost:8765`

## API Endpoints

### Core Endpoints
- **GET /status** - Check service and Whisper model status
- **POST /start-recording** - Start manual audio recording
- **POST /stop-recording** - Stop recording and transcribe
- **GET /transcription** - Get last transcription result
- **POST /config** - Update Whisper model configuration

### Listen Mode (Wake Word Detection)
- **POST /listen-mode/enable** - Enable continuous listening for "Obsidian Note" / "Obsidian Stop"
- **POST /listen-mode/disable** - Disable listen mode
- **GET /streaming-chunks** - Get real-time transcription chunks (for streaming mode)

### Audio Device Selection
- **GET /audio-devices** - List all available input devices
- **POST /audio-device** - Set the microphone to use

## Testing

### Using test_api.html
Open `E:\Transcribe\test_api.html` in your browser for an interactive testing interface.

### Using curl
```bash
# Check status
curl http://localhost:8765/status

# Get available microphones
curl http://localhost:8765/audio-devices

# Start manual recording
curl -X POST http://localhost:8765/start-recording

# Stop recording (after speaking)
curl -X POST http://localhost:8765/stop-recording

# Get transcription
curl http://localhost:8765/transcription

# Enable wake word listening
curl -X POST http://localhost:8765/listen-mode/enable

# Disable wake word listening
curl -X POST http://localhost:8765/listen-mode/disable
```

### Using test scripts
```bash
# Test audio device detection
venv\Scripts\python.exe test_devices.py

# Test whisper model loading
venv\Scripts\python.exe whisper_client.py
```

## Features

### Wake Word Detection
- Continuously listens for "Obsidian Note" to start recording
- Listens for "Obsidian Stop" to end recording
- Uses 3-second audio chunks for detection
- Background operation while you work in other programs

### Real-time Streaming Transcription
- Transcribes audio in ~3-second chunks
- Sends chunks to Obsidian as you speak
- No waiting for full recording to complete

### Microphone Selection
- Supports all audio input devices (physical and virtual)
- USB microphones, Bluetooth headsets, virtual audio cables
- Switch devices without restarting service

## Architecture

```
service.py              - Main Flask server
whisper_client.py       - Faster-whisper integration
wake_word_listener.py   - Wake word detection logic
test_devices.py         - Audio device testing
```

## Troubleshooting

### Model not loading
The faster-whisper model downloads automatically on first use. Check the console for download progress.

If you see errors:
```bash
venv\Scripts\python.exe whisper_client.py
```

### Audio device errors
```bash
# List all audio devices
venv\Scripts\python.exe test_devices.py

# Check available devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Make sure:
- Microphone is connected
- Audio permissions are granted in Windows Settings
- Device is not in use by another application

### Wake word not detecting
1. Check the backend console - you'll see what it's hearing
2. Speak clearly and close to the microphone
3. Upgrade model in service.py line 275:
   ```python
   init_whisper(model_size="medium.en")  # Better accuracy
   ```

### High CPU usage
- Try a smaller model: `tiny` or `base.en`
- Default is `small.en` which balances accuracy and performance

## Configuration

Default configuration:
- **Port**: 8765
- **Whisper Model**: small.en (244MB)
- **Sample Rate**: 16kHz
- **Channels**: Mono
- **Chunk Duration**: 3 seconds
- **Wake Phrase**: "Obsidian Note"
- **Stop Phrase**: "Obsidian Stop"

### Changing Whisper Model

Edit `service.py` line 275:

```python
# Options: tiny, base.en, small.en, medium.en, large
init_whisper(model_size="small.en")
```

Model sizes and accuracy:
- **tiny** (39MB) - Fast, basic accuracy
- **base.en** (74MB) - Good for simple dictation
- **small.en** (244MB) - Default, excellent accuracy ✓
- **medium.en** (769MB) - Very high accuracy, slower
- **large** (1550MB) - Best accuracy, slowest

## Dependencies

From `requirements.txt`:
- flask - Web server
- flask-cors - CORS support for Obsidian plugin
- requests - HTTP client
- sounddevice - Audio capture
- numpy - Array processing
- faster-whisper - Whisper model inference

All dependencies use binary wheels only (no C++ compilation required).

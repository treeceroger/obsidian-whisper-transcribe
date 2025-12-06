# Voice Transcription Backend Service

Lightweight Python service that handles audio recording and transcription using Ollama.

## Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running
3. **dimavz/whisper-tiny** model loaded in Ollama

## Installation

### 1. Install Ollama Model

```bash
ollama pull dimavz/whisper-tiny
```

### 2. Install Python Dependencies

**Option A: Automatic (Windows)**
```bash
# Just run the start script - it will create venv and install dependencies
start.bat
```

**Option B: Manual**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
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

- **GET /status** - Check service and Ollama status
- **POST /start-recording** - Start audio recording
- **POST /stop-recording** - Stop recording and transcribe
- **GET /transcription** - Get last transcription result
- **POST /config** - Update Ollama configuration

## Testing

You can test the service with curl:

```bash
# Check status
curl http://localhost:8765/status

# Start recording
curl -X POST http://localhost:8765/start-recording

# Stop recording (after speaking)
curl -X POST http://localhost:8765/stop-recording

# Get transcription
curl http://localhost:8765/transcription
```

## Troubleshooting

### Ollama not connected
- Make sure Ollama is running: `ollama serve`
- Check Ollama is accessible: `curl http://localhost:11434/api/tags`

### Model not available
- Pull the model: `ollama pull dimavz/whisper-tiny`
- Verify: `ollama list`

### Audio device errors
- Make sure your microphone is connected
- Check audio permissions on your system
- Try listing available devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`

## Configuration

Default configuration:
- **Port**: 8765
- **Ollama URL**: http://localhost:11434
- **Model**: dimavz/whisper-tiny
- **Sample Rate**: 16kHz
- **Channels**: Mono

You can update Ollama configuration at runtime using the `/config` endpoint.

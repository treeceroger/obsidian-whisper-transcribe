# Voice-to-Obsidian Transcription Application Requirements

## Overview
A lightweight voice-activated Obsidian plugin that listens for keyword commands, transcribes speech to text using faster-whisper (small.en model), and appends entries to a note file with timestamps in real-time.

**CRITICAL REQUIREMENTS**:
- Application must run as an Obsidian plugin
- Use faster-whisper library with small.en model (no Ollama required)
- Real-time streaming transcription
- Lightweight implementation for personal use only
- Simple deployment to multiple personal computers
- Support microphone selection

## Functional Requirements

### 1. Wake Word Detection ✅ IMPLEMENTED
- **FR-1.1**: Application must continuously listen for the wake phrase "Obsidian Note"
- **FR-1.2**: Must operate in the background without interfering with other applications
- **FR-1.3**: Wake word detection must be local (no cloud dependencies)
- **FR-1.4**: Must have low false-positive rate to avoid accidental triggers
- **FR-1.5**: Visual indicator (ear icon) shows when listening mode is active

### 2. Voice Recording & Transcription ✅ IMPLEMENTED
- **FR-2.1**: Upon detecting wake phrase, begin recording audio input
- **FR-2.2**: Provide visual/audio feedback that recording has started
- **FR-2.3**: Transcribe audio to text using local speech-to-text model (faster-whisper)
- **FR-2.4**: Continue recording until stop phrase is detected
- **FR-2.5**: Listen for stop phrase "Obsidian Stop" to end transcription
- **FR-2.6**: Stream transcription chunks in real-time (~3 second intervals)

### 3. Obsidian Integration ✅ IMPLEMENTED
- **FR-3.1**: Append transcribed text to a designated Obsidian note file
- **FR-3.2**: Each note entry must include a timestamp in format: `[YYYY-MM-DD HH:MM:SS]`
- **FR-3.3**: All notes should be stored in the same file
- **FR-3.4**: Preserve existing file content when appending new entries
- **FR-3.5**: Support configurable Obsidian vault path
- **FR-3.6**: Support configurable target note filename
- **FR-3.7**: Stream chunks in real-time to Obsidian as user speaks

### 4. Note Format ✅ IMPLEMENTED
- **FR-4.1**: Each entry format:
  ```
  ## [YYYY-MM-DD HH:MM:SS]
  [Transcribed text content appears in real-time]

  ```
- **FR-4.2**: Entries should be separated by blank lines for readability

### 5. Obsidian Plugin Integration ✅ IMPLEMENTED
- **FR-5.1**: Must be installable as an Obsidian community plugin or manually installed plugin
- **FR-5.2**: Plugin settings panel within Obsidian for configuration
- **FR-5.3**: Status indicator in Obsidian UI showing listening/recording/processing states
- **FR-5.4**: Ribbon icons for microphone and listen mode controls
- **FR-5.5**: Plugin must integrate with Obsidian's file system API
- **FR-5.6**: Compatible with Obsidian desktop application (Windows/Mac/Linux)
- **FR-5.7**: Pre-compiled JavaScript (no Node.js build step required)

### 6. Microphone Selection ✅ IMPLEMENTED
- **FR-6.1**: Display all available input devices in plugin settings
- **FR-6.2**: Allow user to select specific microphone
- **FR-6.3**: Support physical and virtual audio devices
- **FR-6.4**: Refresh devices list on demand
- **FR-6.5**: Auto-restart listening when device changes

## Technical Requirements

### 1. Speech Recognition ✅ IMPLEMENTED
- **TR-1.1**: Use faster-whisper library directly (no Ollama)
- **TR-1.2**: Default model: small.en (244MB)
- **TR-1.3**: Support for English language (configurable for others)
- **TR-1.4**: Accept WAV audio format for transcription
- **TR-1.5**: Model downloads automatically on first use
- **TR-1.6**: CPU-based inference with int8 quantization

### 2. Wake Word Detection ✅ IMPLEMENTED
- **TR-2.1**: Use continuous 3-second chunk transcription for wake word detection
- **TR-2.2**: Wake phrases: "Obsidian Note" / "Obsidian Stop"
- **TR-2.3**: Reasonable CPU usage during listening
- **TR-2.4**: Upgrade to medium.en model for better accuracy if needed

### 3. Audio Processing ✅ IMPLEMENTED
- **TR-3.1**: Support all audio input devices via sounddevice library
- **TR-3.2**: Sample rate: 16kHz
- **TR-3.3**: Audio format: WAV (16-bit PCM)
- **TR-3.4**: Mono channel audio
- **TR-3.5**: Device selection via plugin settings
- **TR-3.6**: Support for virtual audio cables

### 4. Platform & Dependencies ✅ IMPLEMENTED
- **TR-4.1**: Platform: Windows (primary), cross-platform capable
- **TR-4.2**: Obsidian desktop application (v0.15.0+)
- **TR-4.3**: Python 3.8+ for backend service
- **TR-4.4**: No Ollama required
- **TR-4.5**: No Node.js required (plugin pre-compiled)
- **TR-4.6**: Minimal dependencies - binary wheels only (no compilation)

### 5. Configuration
- **TR-5.1**: Plugin settings accessible via Obsidian settings panel:
  - Target note filename (default: "Voice Notes.md")
  - Wake phrase (default: "computer start note")
  - Stop phrase (default: "computer end note")
  - Backend service URL (default: http://localhost:8765)
  - Ollama URL (default: http://localhost:11434)
  - Ollama model name (default: dimavz/whisper-tiny)
  - Enable/disable auto-start listening
- **TR-5.2**: Settings stored in Obsidian's data.json format
- **TR-5.3**: Simple default configuration that works out-of-the-box

### 6. Obsidian Plugin Architecture
- **TR-6.1**: Plugin frontend written in TypeScript using Obsidian API
- **TR-6.2**: Manifest.json following Obsidian plugin specifications
- **TR-6.3**: Must include styles.css for UI components
- **TR-6.4**: Plugin must handle lifecycle events (load, unload, enable, disable)

## Non-Functional Requirements

### 1. Performance
- **NFR-1.1**: Wake word detection latency: <500ms
- **NFR-1.2**: Transcription start time: <2 seconds after wake phrase
- **NFR-1.3**: File write latency: <1 second after stop phrase

### 2. Reliability
- **NFR-2.1**: Application should recover from transcription errors
- **NFR-2.2**: Handle audio device disconnection gracefully
- **NFR-2.3**: Prevent data loss if Obsidian file is locked/in-use

### 3. Usability
- **NFR-3.1**: Simple startup process (single command or executable)
- **NFR-3.2**: Clear status indicators (listening, recording, processing, error states)
- **NFR-3.3**: Minimal configuration required for basic usage
- **NFR-3.4**: Helpful error messages

### 4. Security & Privacy
- **NFR-4.1**: All processing must be local (no cloud services)
- **NFR-4.2**: No audio data stored permanently except transcriptions
- **NFR-4.3**: Temporary audio files deleted after transcription

## Technical Architecture Considerations

### Architecture Overview - Lightweight Personal Use

**Simple 2-Component Architecture**:

**Frontend (Obsidian Plugin)**:
- Minimal TypeScript plugin running within Obsidian
- Handles UI, settings, file writing via Obsidian API
- HTTP client to communicate with backend

**Backend (Lightweight Python Service)**:
- Small Python script handling audio capture and wake word detection
- Calls Ollama API for transcription (no local Whisper installation needed!)
- Simple REST API for plugin communication
- Runs as background process

### Recommended Stack (Simplified)

**Plugin (TypeScript)**:
1. **Language**: TypeScript with Obsidian API
2. **Build Tool**: esbuild (fast, simple)
3. **Communication**: fetch() API to backend
4. **File I/O**: Obsidian Vault API
5. **Dependencies**: Minimal - just Obsidian typings

**Backend Service (Python)**:
1. **Framework**: Flask (lightweight) or simple http.server
2. **Wake Word Detection**: pvporcupine (free tier custom wake word)
3. **Audio Recording**: sounddevice + scipy (for WAV)
4. **Speech-to-Text**: Ollama API client (requests library)
5. **Port**: localhost:8765 (configurable)
6. **Total Python dependencies**: ~5 packages

### Communication Protocol
**Plugin ↔ Backend**:
- **REST API** (simple HTTP):
  - GET /status - Check if backend is running
  - POST /start-recording - Begin voice capture
  - POST /stop-recording - End capture and get transcription
  - GET /transcription - Retrieve last transcription
- **Data Format**: JSON
- **Error Handling**: HTTP status codes

**Backend ↔ Ollama**:
- HTTP POST to Ollama API endpoint
- Send audio file for transcription
- Receive transcribed text

### Ollama Integration
**Using dimavz/whisper-tiny**:
- Ollama handles the Whisper model hosting
- Backend sends audio to Ollama via HTTP
- No need to manage Whisper models directly
- Lightweight - offloads heavy ML work to Ollama
- Simple API: POST audio → receive text

## Project Structure (Simplified for Personal Use)

```
obsidian-voice-notes/
├── plugin/                          # Obsidian plugin (TypeScript)
│   ├── src/
│   │   ├── main.ts                  # Plugin entry point
│   │   ├── settings.ts              # Settings panel
│   │   └── backendClient.ts         # Backend API client
│   ├── styles.css                   # Plugin styles
│   ├── manifest.json                # Obsidian plugin manifest
│   ├── package.json                 # Node.js dependencies
│   ├── tsconfig.json                # TypeScript configuration
│   └── esbuild.config.mjs           # Build configuration
│
├── backend/                         # Python backend service
│   ├── service.py                   # Main service (Flask + audio + wake word)
│   ├── ollama_client.py             # Ollama API client
│   ├── requirements.txt             # Python dependencies (~5 packages)
│   └── start.bat                    # Windows startup script
│
├── install.md                       # Simple installation guide
└── README.md                        # Quick start guide
```

**Key Simplifications**:
- Single Python file for backend (or 2-3 small files)
- Minimal plugin structure
- Simple .bat file to start backend on Windows
- No complex build scripts or installers

## User Stories

**US-1**: As a user, I want to trigger note-taking hands-free while working on other tasks

**US-2**: As a user, I want all my voice notes in one Obsidian file for easy reference

**US-3**: As a user, I want timestamps on each note to know when I recorded them

**US-4**: As a user, I want the system to run locally without internet dependency

**US-5**: As a user, I want to easily start and stop recording with voice commands

**US-6**: As an Obsidian user, I want to install this as a plugin so I can manage it alongside my other plugins

**US-7**: As a user, I want to configure settings within Obsidian's interface rather than editing config files

**US-8**: As a user, I want to see the listening/recording status in the Obsidian UI

## Implementation Challenges & Considerations

### Plugin-Specific Challenges
1. **Obsidian API Limitations**:
   - Obsidian runs in Electron, which has security restrictions
   - Direct microphone access may require workarounds or native modules
   - File system access is sandboxed to the vault directory

2. **Backend Communication**:
   - Plugin must handle backend service not running gracefully
   - Need connection retry logic and timeout handling
   - CORS considerations for localhost HTTP requests

3. **Cross-Platform Compatibility**:
   - Audio device APIs differ between Windows/Mac/Linux
   - File path handling varies by OS
   - Backend service installation differs per platform

4. **Wake Word Detection**:
   - Continuous listening requires persistent backend process
   - Cannot rely solely on Obsidian plugin (which may be inactive)
   - Backend must run independently of Obsidian lifecycle

5. **User Experience**:
   - Plugin should provide clear feedback if backend is offline
   - Settings should validate backend connection
   - Consider manual trigger option if wake word fails

### Recommended Development Phases (Simplified)

**Phase 1: Backend MVP**
- Python service with Flask
- Audio recording with sounddevice
- Ollama API integration for transcription
- Simple REST endpoint for manual recording (no wake word yet)

**Phase 2: Basic Plugin**
- Obsidian plugin structure and manifest
- Settings panel with minimal options
- Backend client communication
- Manual button to start/stop recording
- Write transcription to configured note file

**Phase 3: Wake Word Integration**
- Add pvporcupine wake word detection to backend
- Continuous listening mode
- Status updates via polling or WebSocket

**Phase 4: Personal Deployment**
- Simple installation instructions
- Windows .bat startup script
- Copy to second computer setup guide

## Deployment & Installation Requirements (Personal Use)

### Plugin Installation
- **DI-1**: Manual installation by copying to .obsidian/plugins folder
- **DI-2**: Plugin files: main.js, manifest.json, styles.css
- **DI-3**: Simple build command (npm run build)

### Backend Service Installation
- **DI-4**: Python venv with pip install -r requirements.txt
- **DI-5**: start.bat script to launch backend
- **DI-6**: Simple instructions to verify Ollama is running

### Prerequisites
- **DI-7**: Ollama installed with dimavz/whisper-tiny model loaded
- **DI-8**: Python 3.8+ installed
- **DI-9**: Obsidian desktop app installed

### Deployment to Second Computer
- **DI-10**: Copy plugin folder to .obsidian/plugins
- **DI-11**: Copy backend folder and run pip install
- **DI-12**: Update Ollama URL in settings if needed
- **DI-13**: Run start.bat and enable plugin

## Success Criteria (Personal Use)

**Phase 1 (Backend MVP)**:
- [ ] Python backend runs and responds to /status endpoint
- [ ] Can record audio and save to WAV file
- [ ] Successfully sends audio to Ollama and receives transcription
- [ ] Basic REST endpoints working

**Phase 2 (Basic Plugin)**:
- [ ] Plugin loads in Obsidian
- [ ] Settings panel accessible and saves configuration
- [ ] Manual record button communicates with backend
- [ ] Transcription appears in configured note file with timestamp
- [ ] Notes append without data loss

**Phase 3 (Wake Word)**:
- [ ] Wake phrase "computer start note" triggers recording
- [ ] Stop phrase "computer end note" ends recording
- [ ] Status indicator shows listening/recording state
- [ ] Reliable triggering for personal use (>85% success rate acceptable)

**Phase 4 (Deployment)**:
- [ ] Successfully deployed to second computer
- [ ] Simple startup process (double-click .bat file)
- [ ] Works with personal Obsidian vault on both computers

## Expected Python Dependencies (Backend)

```txt
flask==3.0.0              # Lightweight web framework
requests==2.31.0          # For Ollama API calls
sounddevice==0.4.6        # Audio recording
scipy==1.11.4             # WAV file writing
pvporcupine==3.0.0        # Wake word detection (free tier)
```

**Total**: ~5 core packages plus their dependencies
**Installation**: `pip install -r requirements.txt`
**Virtual environment recommended**: `python -m venv venv`

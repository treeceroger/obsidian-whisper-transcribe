"""
Lightweight Flask service for voice recording and transcription
Handles audio capture and communicates with Ollama for transcription
"""
import os
import tempfile
import threading
import time
import wave
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import sounddevice as sd
import numpy as np

from whisper_client import WhisperClient
from wake_word_listener import WakeWordListener


app = Flask(__name__)
CORS(app)  # Enable CORS for Obsidian plugin communication

# Configuration
SAMPLE_RATE = 16000  # 16kHz sample rate
CHANNELS = 1  # Mono audio
TEMP_DIR = tempfile.gettempdir()

# Global state
recording_state = {
    'is_recording': False,
    'audio_data': [],
    'last_transcription': None,
    'error': None
}

# Wake word listener state
listen_mode_state = {
    'enabled': False,
    'is_listening': False,
    'is_recording_from_wake': False
}

# Initialize Whisper client
whisper_client = None
wake_listener = None


def init_whisper(model_size: str = "base.en"):
    """Initialize Whisper client with configuration"""
    global whisper_client, wake_listener
    whisper_client = WhisperClient(model_size=model_size)

    # Initialize wake word listener
    if whisper_client:
        wake_listener = WakeWordListener(
            whisper_client,
            wake_phrase="obsidian note",
            stop_phrase="obsidian stop"
        )
        # Set up callbacks
        wake_listener.on_wake_detected = on_wake_phrase_detected
        wake_listener.on_stop_detected = on_stop_phrase_detected
        wake_listener.on_transcription_complete = on_wake_transcription_complete


def on_wake_phrase_detected():
    """Callback when wake phrase is detected"""
    global listen_mode_state
    listen_mode_state['is_recording_from_wake'] = True
    print("[SERVICE] Wake phrase detected - recording started")


def on_stop_phrase_detected():
    """Callback when stop phrase is detected"""
    global listen_mode_state
    listen_mode_state['is_recording_from_wake'] = False
    print("[SERVICE] Stop phrase detected - recording stopped")


def on_wake_transcription_complete(transcription: str):
    """Callback when wake word transcription is complete"""
    global recording_state
    recording_state['last_transcription'] = transcription
    print(f"[SERVICE] Wake word transcription complete: {transcription}")


def audio_callback(indata, frames, time_info, status):
    """Callback function for audio recording"""
    if status:
        print(f"Audio status: {status}")
    if recording_state['is_recording']:
        recording_state['audio_data'].append(indata.copy())


@app.route('/status', methods=['GET'])
def status():
    """Check service and Whisper status"""
    whisper_ready = whisper_client.check_health() if whisper_client else False

    return jsonify({
        'service': 'running',
        'ollama_connected': whisper_ready,  # Keep same key for compatibility with plugin
        'model_available': whisper_ready,
        'is_recording': recording_state['is_recording'] or listen_mode_state['is_recording_from_wake'],
        'listen_mode_enabled': listen_mode_state['enabled'],
        'listen_mode_listening': listen_mode_state['is_listening'],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/listen-mode/enable', methods=['POST'])
def enable_listen_mode():
    """Enable continuous listening for wake words"""
    global listen_mode_state

    if not wake_listener:
        return jsonify({'error': 'Wake word listener not initialized'}), 500

    if listen_mode_state['enabled']:
        return jsonify({'status': 'already_enabled'})

    wake_listener.start_listening()
    listen_mode_state['enabled'] = True
    listen_mode_state['is_listening'] = True

    return jsonify({
        'status': 'enabled',
        'wake_phrase': 'Obsidian Note',
        'stop_phrase': 'Obsidian Stop'
    })


@app.route('/listen-mode/disable', methods=['POST'])
def disable_listen_mode():
    """Disable continuous listening for wake words"""
    global listen_mode_state

    if not wake_listener:
        return jsonify({'error': 'Wake word listener not initialized'}), 500

    if not listen_mode_state['enabled']:
        return jsonify({'status': 'already_disabled'})

    wake_listener.stop_listening()
    listen_mode_state['enabled'] = False
    listen_mode_state['is_listening'] = False
    listen_mode_state['is_recording_from_wake'] = False

    return jsonify({'status': 'disabled'})


@app.route('/start-recording', methods=['POST'])
def start_recording():
    """Start audio recording"""
    if recording_state['is_recording']:
        return jsonify({'error': 'Already recording'}), 400

    # Reset state
    recording_state['is_recording'] = True
    recording_state['audio_data'] = []
    recording_state['error'] = None
    recording_state['last_transcription'] = None

    return jsonify({
        'status': 'recording',
        'message': 'Recording started'
    })


@app.route('/stop-recording', methods=['POST'])
def stop_recording():
    """Stop recording and transcribe audio"""
    if not recording_state['is_recording']:
        return jsonify({'error': 'Not currently recording'}), 400

    recording_state['is_recording'] = False

    # Check if we have audio data
    if not recording_state['audio_data']:
        return jsonify({'error': 'No audio data recorded'}), 400

    try:
        # Combine all audio chunks
        audio_array = np.concatenate(recording_state['audio_data'], axis=0)

        # Save to temporary WAV file
        temp_audio_path = os.path.join(TEMP_DIR, f'voice_note_{int(time.time())}.wav')

        # Write WAV file using wave module
        with wave.open(temp_audio_path, 'wb') as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)  # 2 bytes for int16
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_array.tobytes())

        print(f"Audio saved to: {temp_audio_path}")

        # Transcribe using Whisper
        if not whisper_client:
            return jsonify({'error': 'Whisper client not initialized'}), 500

        transcription = whisper_client.transcribe_audio(temp_audio_path)

        # Clean up temp file
        try:
            os.remove(temp_audio_path)
        except:
            pass

        if transcription:
            recording_state['last_transcription'] = transcription
            return jsonify({
                'status': 'completed',
                'transcription': transcription,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Transcription failed'}), 500

    except Exception as e:
        recording_state['error'] = str(e)
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


@app.route('/transcription', methods=['GET'])
def get_last_transcription():
    """Get the last transcription result"""
    if recording_state['last_transcription']:
        return jsonify({
            'transcription': recording_state['last_transcription'],
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({'error': 'No transcription available'}), 404


@app.route('/config', methods=['POST'])
def update_config():
    """Update Whisper configuration"""
    data = request.json
    model_size = data.get('model', 'tiny').split('/')[-1].split('-')[-1]  # Extract size from model name

    init_whisper(model_size)

    return jsonify({
        'status': 'updated',
        'model': model_size
    })


def start_audio_stream():
    """Start the audio input stream"""
    print("Starting audio stream...")
    with sd.InputStream(
        callback=audio_callback,
        channels=CHANNELS,
        samplerate=SAMPLE_RATE,
        dtype=np.int16
    ):
        print("Audio stream started. Press Ctrl+C to stop.")
        # Keep the stream open
        while True:
            time.sleep(0.1)


if __name__ == '__main__':
    print("=" * 50)
    print("Voice Transcription Backend Service")
    print("=" * 50)

    # Initialize Whisper client
    print("\nInitializing Whisper model...")
    # Options: tiny, base, small, medium, large
    # Recommended: small for good balance of speed and accuracy
    init_whisper(model_size="base.en")

    # Check Whisper status
    if whisper_client and whisper_client.check_health():
        print("[OK] Whisper tiny model loaded and ready")
    else:
        print("[WARN] Whisper model failed to load")
        print("  The model will download automatically on first use")

    # Start audio stream in background thread
    audio_thread = threading.Thread(target=start_audio_stream, daemon=True)
    audio_thread.start()

    # Start Flask server
    print("\nStarting Flask server on http://localhost:8765")
    print("API Endpoints:")
    print("  GET  /status           - Check service status")
    print("  POST /start-recording  - Start recording")
    print("  POST /stop-recording   - Stop recording and transcribe")
    print("  GET  /transcription    - Get last transcription")
    print("  POST /config           - Update Ollama config")
    print("=" * 50)

    app.run(host='localhost', port=8765, debug=False)

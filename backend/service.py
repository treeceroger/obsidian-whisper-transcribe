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
    'is_recording_from_wake': False,
    'streaming_chunks': [],  # Buffer for streaming chunks
    'last_chunk_id': 0  # Incrementing ID for chunks
}

# Audio device configuration
audio_config = {
    'device_id': None  # None = use default device
}

# Initialize Whisper client
whisper_client = None
wake_listener = None
audio_stream = None


def init_whisper(model_size: str = "small.en"):
    """Initialize Whisper client with configuration"""
    global whisper_client, wake_listener
    whisper_client = WhisperClient(model_size=model_size)

    # Initialize wake word listener
    if whisper_client:
        wake_listener = WakeWordListener(
            whisper_client,
            wake_phrase="obsidian note",
            stop_phrase="obsidian stop",
            streaming_mode=True,  # Enable streaming mode
            device_id=audio_config['device_id']  # Use configured device
        )
        # Set up callbacks
        wake_listener.on_wake_detected = on_wake_phrase_detected
        wake_listener.on_stop_detected = on_stop_phrase_detected
        wake_listener.on_transcription_complete = on_wake_transcription_complete
        wake_listener.on_chunk_transcribed = on_chunk_transcribed  # Streaming callback


def on_wake_phrase_detected():
    """Callback when wake phrase is detected"""
    global listen_mode_state
    listen_mode_state['is_recording_from_wake'] = True
    listen_mode_state['streaming_chunks'] = []  # Clear chunks for new recording
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


def on_chunk_transcribed(chunk: str):
    """Callback when a chunk is transcribed in streaming mode"""
    global listen_mode_state
    listen_mode_state['last_chunk_id'] += 1
    chunk_data = {
        'id': listen_mode_state['last_chunk_id'],
        'text': chunk,
        'timestamp': datetime.now().isoformat()
    }
    listen_mode_state['streaming_chunks'].append(chunk_data)

    # Keep only last 100 chunks to prevent memory issues
    if len(listen_mode_state['streaming_chunks']) > 100:
        listen_mode_state['streaming_chunks'] = listen_mode_state['streaming_chunks'][-100:]

    print(f"[SERVICE] Chunk transcribed: {chunk}")


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
    model_name = whisper_client.model_size if whisper_client else None

    return jsonify({
        'service': 'running',
        'whisper_ready': whisper_ready,
        'model_available': whisper_ready,
        'model_name': model_name,
        'is_recording': recording_state['is_recording'] or listen_mode_state['is_recording_from_wake'],
        'listen_mode_enabled': listen_mode_state['enabled'],
        'listen_mode_listening': listen_mode_state['is_listening'],
        'selected_device_id': audio_config['device_id'],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/audio-devices', methods=['GET'])
def get_audio_devices():
    """Get list of available audio input devices"""
    try:
        devices = sd.query_devices()
        input_devices = []

        # Get default input device index
        try:
            default_input_device = sd.default.device[0] if isinstance(sd.default.device, (list, tuple)) else None
        except:
            default_input_device = None

        for idx, device in enumerate(devices):
            # Only include input devices (with input channels)
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'id': idx,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': int(device['default_samplerate']),
                    'is_default': idx == default_input_device if default_input_device is not None else False
                })

        print(f"[AUDIO] Found {len(input_devices)} input devices")

        return jsonify({
            'devices': input_devices,
            'selected_device_id': audio_config['device_id']
        })
    except Exception as e:
        print(f"[AUDIO] Error querying devices: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to query audio devices: {str(e)}'}), 500


@app.route('/audio-device', methods=['POST'])
def set_audio_device():
    """Set the audio input device to use"""
    global audio_config, wake_listener

    data = request.json
    device_id = data.get('device_id')

    # Validate device_id
    if device_id is not None:
        try:
            devices = sd.query_devices()
            if device_id < 0 or device_id >= len(devices):
                return jsonify({'error': 'Invalid device ID'}), 400

            device = devices[device_id]
            if device['max_input_channels'] <= 0:
                return jsonify({'error': 'Device is not an input device'}), 400

        except Exception as e:
            return jsonify({'error': f'Failed to validate device: {str(e)}'}), 500

    # Update configuration
    audio_config['device_id'] = device_id

    # Restart wake listener if it's running
    if wake_listener and listen_mode_state['enabled']:
        wake_listener.stop_listening()
        wake_listener.device_id = device_id
        wake_listener.start_listening()

    return jsonify({
        'status': 'updated',
        'device_id': device_id
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


@app.route('/streaming-chunks', methods=['GET'])
def get_streaming_chunks():
    """Get streaming transcription chunks since last check"""
    since_id = request.args.get('since_id', 0, type=int)

    # Get chunks with ID greater than since_id
    new_chunks = [
        chunk for chunk in listen_mode_state['streaming_chunks']
        if chunk['id'] > since_id
    ]

    return jsonify({
        'chunks': new_chunks,
        'latest_id': listen_mode_state['last_chunk_id'],
        'is_recording': listen_mode_state['is_recording_from_wake']
    })


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
    global audio_stream
    print("Starting audio stream...")
    device_name = "default" if audio_config['device_id'] is None else f"device {audio_config['device_id']}"
    print(f"Using audio device: {device_name}")

    with sd.InputStream(
        device=audio_config['device_id'],  # Use configured device
        callback=audio_callback,
        channels=CHANNELS,
        samplerate=SAMPLE_RATE,
        dtype=np.int16
    ) as stream:
        audio_stream = stream
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
    # Options: tiny, base.en, small.en, medium.en, large
    # Upgraded to small.en for better wake word recognition
    init_whisper(model_size="small.en")

    # Check Whisper status
    if whisper_client and whisper_client.check_health():
        print("[OK] Whisper small.en model loaded and ready")
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

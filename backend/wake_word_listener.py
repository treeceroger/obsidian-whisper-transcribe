"""
Wake word listener using continuous audio monitoring
Detects wake phrase "computer take note" and stop phrase "computer end note"
"""
import threading
import time
import wave
import tempfile
import os
import queue
import sounddevice as sd
import numpy as np
from whisper_client import WhisperClient


class WakeWordListener:
    def __init__(self, whisper_client: WhisperClient,
                 wake_phrase: str = "computer take note",
                 stop_phrase: str = "computer end note",
                 streaming_mode: bool = True,
                 device_id: int = None):
        """
        Initialize wake word listener

        Args:
            whisper_client: WhisperClient instance for transcription
            wake_phrase: Phrase to start recording
            stop_phrase: Phrase to stop recording
            streaming_mode: If True, transcribe and stream chunks in real-time
            device_id: Audio input device ID (None = use default)
        """
        self.whisper_client = whisper_client
        self.wake_phrase = wake_phrase.lower()
        self.stop_phrase = stop_phrase.lower()
        self.streaming_mode = streaming_mode
        self.device_id = device_id

        self.is_listening = False
        self.is_recording = False
        self.process_thread = None
        self.audio_stream = None

        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 3  # Process in 3-second chunks

        # Buffers and Queues
        self.audio_queue = queue.Queue()
        self.full_recording_buffer = []  # Stores audio while in recording mode
        self.streaming_transcription = []  # Accumulates streamed chunks

        # Callbacks
        self.on_wake_detected = None
        self.on_stop_detected = None
        self.on_transcription_complete = None
        self.on_chunk_transcribed = None  # New: for streaming chunks

    def start_listening(self):
        """Start continuous listening for wake word"""
        if self.is_listening:
            print("Already listening")
            return

        self.is_listening = True
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.full_recording_buffer = []
        self.streaming_transcription = []
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_audio_queue, daemon=True)
        self.process_thread.start()
        
        # Start audio stream
        try:
            self.audio_stream = sd.InputStream(
                device=self.device_id,  # Use specified device or default
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback,
                dtype=np.int16,
                blocksize=int(self.sample_rate * 0.5)  # 0.5s blocks for responsiveness
            )
            self.audio_stream.start()
            device_name = "default" if self.device_id is None else f"device {self.device_id}"
            print(f"[WAKE WORD] Started listening for '{self.wake_phrase}' on {device_name}")
        except Exception as e:
            print(f"[WAKE WORD] Error starting audio stream: {e}")
            self.is_listening = False

    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        self.is_recording = False
        
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
            
        if self.process_thread:
            self.process_thread.join(timeout=2)
            
        print("[WAKE WORD] Stopped listening")

    def _audio_callback(self, indata, frames, time, status):
        """Callback for sounddevice input stream"""
        if status:
            print(f"[WAKE WORD] Audio status: {status}")
        if self.is_listening:
            self.audio_queue.put(indata.copy())

    def _process_audio_queue(self):
        """Main loop to process audio from the queue"""
        current_chunk_buffer = []
        samples_per_chunk = int(self.sample_rate * self.chunk_duration)
        current_samples = 0
        
        while self.is_listening:
            try:
                # Get audio data from queue (blocking with timeout)
                try:
                    data = self.audio_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Add to current processing buffer
                current_chunk_buffer.append(data)
                current_samples += len(data)
                
                # If we are recording, ALSO add to the full recording buffer
                if self.is_recording:
                    self.full_recording_buffer.append(data)
                
                # Check if we have enough data for a transcription chunk
                if current_samples >= samples_per_chunk:
                    # Combine buffer into one array
                    audio_chunk = np.concatenate(current_chunk_buffer)
                    
                    # Reset buffer (sliding window could be better, but keeping simple for now)
                    current_chunk_buffer = []
                    current_samples = 0
                    
                    # Transcribe this chunk
                    transcription = self._transcribe_chunk(audio_chunk)
                    
                    if transcription:
                        self._handle_transcription(transcription)
                        
            except Exception as e:
                print(f"[WAKE WORD] Error in process loop: {e}")
                time.sleep(0.5)

    def _handle_transcription(self, transcription: str):
        """Handle the transcription result"""
        transcription_lower = transcription.lower().strip()
        print(f"[WAKE WORD] Heard: {transcription}")

        # Check for wake phrase
        if not self.is_recording and self.wake_phrase in transcription_lower:
            print(f"[WAKE WORD] Wake phrase detected!")
            self.is_recording = True
            self.full_recording_buffer = [] # Start fresh recording
            self.streaming_transcription = []  # Reset streaming buffer
            if self.on_wake_detected:
                self.on_wake_detected()

        # Check for stop phrase
        elif self.is_recording and self.stop_phrase in transcription_lower:
            print(f"[WAKE WORD] Stop phrase detected!")
            self.is_recording = False

            if self.on_stop_detected:
                self.on_stop_detected()

            # In streaming mode, we've already sent chunks, just signal completion
            if self.streaming_mode:
                if self.on_transcription_complete:
                    # Send final aggregated transcription (optional, for reference)
                    full_text = " ".join(self.streaming_transcription)
                    self.on_transcription_complete(self._clean_transcription(full_text))
            else:
                # Batch mode: Get full transcription of recorded audio
                full_transcription = self._process_recording()
                if self.on_transcription_complete and full_transcription:
                    self.on_transcription_complete(full_transcription)

            self.full_recording_buffer = []
            self.streaming_transcription = []

        # During recording: handle chunk streaming
        elif self.is_recording:
            if self.streaming_mode and self.on_chunk_transcribed:
                # Clean the chunk (remove wake/stop phrases if present)
                clean_chunk = transcription_lower.replace(self.wake_phrase, '').replace(self.stop_phrase, '').strip()
                if clean_chunk:
                    self.streaming_transcription.append(clean_chunk)
                    # Emit chunk in real-time
                    print(f"[WAKE WORD] Streaming chunk: {clean_chunk}")
                    self.on_chunk_transcribed(clean_chunk)

    def _clean_transcription(self, text: str) -> str:
        """Remove wake and stop phrases from transcription and capitalize"""
        if not text:
            return ""

        # Remove the wake phrase
        text = text.lower().replace(self.wake_phrase, '').strip()
        # Remove the stop phrase
        text = text.replace(self.stop_phrase, '').strip()
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]

        return text

    def _transcribe_chunk(self, audio_chunk: np.ndarray) -> str:
        """Transcribe a small audio chunk"""
        try:
            # Save chunk to temporary file
            temp_path = os.path.join(tempfile.gettempdir(), f'wake_chunk_{int(time.time())}_{id(audio_chunk)}.wav')

            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_chunk.tobytes())

            # Quick transcription
            transcription = self.whisper_client.transcribe_audio(temp_path)

            # Clean up
            try:
                os.remove(temp_path)
            except:
                pass

            return transcription

        except Exception as e:
            print(f"[WAKE WORD] Chunk transcription error: {e}")
            return None

    def _process_recording(self) -> str:
        """Process the full recording buffer"""
        if not self.full_recording_buffer:
            return None

        try:
            # Combine all chunks
            full_audio = np.concatenate(self.full_recording_buffer, axis=0)

            # Save to temp file
            temp_path = os.path.join(tempfile.gettempdir(), f'full_recording_{int(time.time())}.wav')

            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(full_audio.tobytes())

            print(f"[WAKE WORD] Transcribing full recording...")

            # Transcribe the full recording
            transcription = self.whisper_client.transcribe_audio(temp_path)

            # Clean up
            try:
                os.remove(temp_path)
            except:
                pass

            # Remove wake and stop phrases from transcription
            if transcription:
                # Remove the wake phrase
                transcription = transcription.lower().replace(self.wake_phrase, '').strip()
                # Remove the stop phrase
                transcription = transcription.lower().replace(self.stop_phrase, '').strip()
                # Capitalize first letter
                if transcription:
                    transcription = transcription[0].upper() + transcription[1:]

            return transcription

        except Exception as e:
            print(f"[WAKE WORD] Full recording processing error: {e}")
            return None


if __name__ == "__main__":
    # Test wake word listener
    from whisper_client import WhisperClient

    whisper = WhisperClient(model_size="small.en")
    listener = WakeWordListener(whisper)

    def on_wake():
        print(">>> Recording started!")

    def on_stop():
        print(">>> Recording stopped!")

    def on_transcription(text):
        print(f">>> Transcription: {text}")

    listener.on_wake_detected = on_wake
    listener.on_stop_detected = on_stop
    listener.on_transcription_complete = on_transcription

    listener.start_listening()

    print("Listening for wake word... (Press Ctrl+C to stop)")
    print(f"Say: '{listener.wake_phrase}'")
    print(f"Then speak your note")
    print(f"Then say: '{listener.stop_phrase}'")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop_listening()
        print("\nStopped")

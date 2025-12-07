"""
Faster-Whisper client for audio transcription
More reliable than Ollama for whisper models
"""
from faster_whisper import WhisperModel
from typing import Optional
import os


class WhisperClient:
    def __init__(self, model_size: str = "small.en", device: str = "cpu"):
        """
        Initialize Faster-Whisper client

        Args:
            model_size: Model size (tiny, base.en, small.en, medium.en, large)
            device: Device to run on (cpu or cuda)
        """
        self.model_size = model_size
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the whisper model"""
        try:
            print(f"Loading Whisper {self.model_size} model...")
            # Download and cache the model automatically
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8"  # Use int8 for CPU efficiency
            )
            print(f"Whisper {self.model_size} model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.model = None

    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file using Faster-Whisper

        Args:
            audio_file_path: Path to audio WAV file

        Returns:
            Transcribed text or None if error
        """
        if not self.model:
            print("Whisper model not loaded")
            return None

        try:
            # Check if file exists
            if not os.path.exists(audio_file_path):
                print(f"Audio file not found: {audio_file_path}")
                return None

            print(f"Transcribing: {audio_file_path}")

            # Transcribe the audio file
            segments, info = self.model.transcribe(
                audio_file_path,
                beam_size=5,
                language="en",  # Set to English, can be made configurable
                condition_on_previous_text=False
            )

            # Combine all segments into one text
            transcription = " ".join([segment.text for segment in segments])

            print(f"Transcription complete: {transcription[:100]}...")
            return transcription.strip()

        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def check_health(self) -> bool:
        """
        Check if Whisper model is loaded and ready

        Returns:
            True if model is loaded, False otherwise
        """
        return self.model is not None


if __name__ == "__main__":
    # Test the Whisper client
    client = WhisperClient(model_size="tiny")

    if client.check_health():
        print("✓ Whisper client is ready")
    else:
        print("✗ Whisper client failed to initialize")

"""
Ollama API client for audio transcription using dimavz/whisper-tiny model
"""
import requests
import base64
import os
from typing import Optional


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "dimavz/whisper-tiny"):
        """
        Initialize Ollama client

        Args:
            base_url: Ollama server URL
            model: Model name to use for transcription
        """
        self.base_url = base_url.rstrip('/')
        self.model = model

    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file using Ollama whisper model

        Args:
            audio_file_path: Path to audio WAV file

        Returns:
            Transcribed text or None if error
        """
        try:
            # Method 1: Try multipart file upload (for whisper models)
            try:
                with open(audio_file_path, 'rb') as f:
                    files = {'file': ('audio.wav', f, 'audio/wav')}
                    data = {'model': self.model}

                    response = requests.post(
                        f"{self.base_url}/api/transcribe",
                        files=files,
                        data=data,
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()
                        transcription = result.get('text', result.get('response', ''))
                        return transcription.strip() if transcription else None
                    elif response.status_code == 404:
                        print("Transcribe endpoint not found, trying alternative method...")
                    else:
                        print(f"Transcribe endpoint error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Multipart upload failed: {e}, trying base64 method...")

            # Method 2: Try base64 with chat endpoint (alternative for some whisper integrations)
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()

            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # Try chat API with prompt
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Transcribe this audio.",
                        "images": [audio_base64]
                    }
                ],
                "stream": False
            }

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                message = result.get('message', {})
                transcription = message.get('content', '')
                return transcription.strip() if transcription else None
            else:
                print(f"Chat API error: {response.status_code} - {response.text}")

            # Method 3: Try generate endpoint as fallback
            payload = {
                "model": self.model,
                "prompt": "Transcribe:",
                "images": [audio_base64],
                "stream": False
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"Generate API error: {response.status_code} - {response.text}")
                return None

        except FileNotFoundError:
            print(f"Audio file not found: {audio_file_path}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def check_health(self) -> bool:
        """
        Check if Ollama server is running and accessible

        Returns:
            True if server is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def check_model_available(self) -> bool:
        """
        Check if the specified model is available in Ollama

        Returns:
            True if model is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                return any(model.get('name') == self.model for model in models)
            return False
        except:
            return False


if __name__ == "__main__":
    # Test the Ollama client
    client = OllamaClient()

    print("Testing Ollama connection...")
    if client.check_health():
        print("✓ Ollama is running")

        if client.check_model_available():
            print(f"✓ Model '{client.model}' is available")
        else:
            print(f"✗ Model '{client.model}' not found")
            print("  Run: ollama pull dimavz/whisper-tiny")
    else:
        print("✗ Ollama is not running or not accessible")
        print("  Make sure Ollama is started")

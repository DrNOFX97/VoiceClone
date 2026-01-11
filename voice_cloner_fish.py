"""
Voice Cloner Module - Fish Speech Backend
Uses Fish Speech S1-mini for voice cloning with better PT-PT support
"""

import os
import torch
import torchaudio
from pathlib import Path
import logging
import requests
import base64
import subprocess
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fish Speech paths
FISH_SPEECH_PATH = Path.home() / "projetos" / "fish-speech"
API_URL = "http://127.0.0.1:8080"


class VoiceCloner:
    """
    Voice cloning system using Fish Speech S1-mini
    Better PT-PT accent preservation than XTTS-v2
    Uses Fish Speech API server
    """

    def __init__(self, device=None):
        """
        Initialize the voice cloner with Fish Speech

        Args:
            device (str): Device to use ('mps', 'cuda', or 'cpu')
        """
        # Determine device
        if device is None:
            if torch.backends.mps.is_available():
                self.device = "mps"
            elif torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        else:
            self.device = device

        logger.info(f"Initializing Fish Speech Voice Cloner on device: {self.device}")

        # Model paths
        self.checkpoint_path = FISH_SPEECH_PATH / "checkpoints" / "openaudio-s1-mini"
        self.venv_python = FISH_SPEECH_PATH / "venv_fish" / "bin" / "python"

        # Verify checkpoints exist
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Fish Speech checkpoints not found at {self.checkpoint_path}")

        # Start API server if not running
        self._ensure_api_server()

        logger.info("Fish Speech Voice Cloner initialized successfully!")

        # Supported languages
        self.supported_languages = {
            'pt': 'Portuguese (PT-PT and PT-BR)',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'ru': 'Russian',
            'nl': 'Dutch',
        }

    def _ensure_api_server(self):
        """Ensure Fish Speech API server is running"""
        try:
            response = requests.get(f"{API_URL}/v1/health", timeout=2)
            if response.status_code == 200:
                logger.info("Fish Speech API server is already running")
                return
        except Exception as e:
            logger.debug(f"API server not responding: {e}")

        logger.info("Starting Fish Speech API server...")
        # Start server in background
        subprocess.Popen(
            [
                str(self.venv_python),
                str(FISH_SPEECH_PATH / "tools" / "api_server.py"),
                "--llama-checkpoint-path", str(self.checkpoint_path),
                "--decoder-checkpoint-path", str(self.checkpoint_path / "codec.pth"),
                "--decoder-config-name", "modded_dac_vq",
                "--device", self.device,
            ],
            cwd=str(FISH_SPEECH_PATH),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for server to start
        for i in range(60):  # Wait up to 60 seconds
            try:
                time.sleep(1)
                response = requests.get(f"{API_URL}/v1/health", timeout=2)
                if response.status_code == 200:
                    logger.info("Fish Speech API server started successfully")
                    return
            except:
                continue

        raise RuntimeError("Failed to start Fish Speech API server")

    def clone_voice(self, text, speaker_wav, language='pt', output_path='output.wav'):
        """
        Clone voice and generate speech using Fish Speech API

        Args:
            text (str): Text to convert to speech
            speaker_wav (str): Path to reference audio file (10-30 seconds recommended)
            language (str): Language code (e.g., 'pt', 'en', 'es')
            output_path (str): Path to save output audio

        Returns:
            str: Path to generated audio file
        """
        try:
            # Validate inputs
            if not os.path.exists(speaker_wav):
                raise FileNotFoundError(f"Speaker audio file not found: {speaker_wav}")

            if language not in self.supported_languages:
                logger.warning(f"Language '{language}' not in common list. Trying anyway...")

            if not text.strip():
                raise ValueError("Text cannot be empty")

            logger.info(f"Generating speech in {self.supported_languages.get(language, language)}...")
            logger.info(f"Text: {text[:50]}..." if len(text) > 50 else f"Text: {text}")
            logger.info(f"Reference audio: {speaker_wav}")

            # Read and encode reference audio
            with open(speaker_wav, 'rb') as f:
                audio_data = f.read()
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')

            # Create API request - Fixed to match ServeTTSRequest schema
            request_data = {
                "text": text,
                "references": [
                    {
                        "audio": audio_b64,  # Base64 string is auto-decoded by ServeReferenceAudio
                        "text": ""  # Auto-detect
                    }
                ],
                "chunk_length": 200,
                "format": "wav",
                "max_new_tokens": 1024,
                "top_p": 0.8,
                "repetition_penalty": 1.1,
                "temperature": 0.8,  # Match schema default
                "normalize": True,
                "use_memory_cache": "off",
                "streaming": False
            }

            # Send request to API
            logger.info("Sending request to Fish Speech API...")
            response = requests.post(
                f"{API_URL}/v1/tts",
                json=request_data,
                timeout=180
            )

            if response.status_code != 200:
                raise RuntimeError(f"API request failed with status {response.status_code}: {response.text}")

            # Save the audio
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Speech generated successfully: {output_path}")
            return str(output_path)

        except requests.Timeout:
            logger.error("Fish Speech API request timed out")
            raise RuntimeError("Speech generation timed out after 180 seconds")
        except Exception as e:
            logger.error(f"Error during voice cloning: {e}")
            raise

    def get_supported_languages(self):
        """
        Get list of supported languages

        Returns:
            dict: Dictionary of language codes and names
        """
        return self.supported_languages

    def validate_audio_duration(self, audio_path, min_duration=10.0):
        """
        Check if audio file meets minimum duration requirement

        Args:
            audio_path (str): Path to audio file
            min_duration (float): Minimum duration in seconds

        Returns:
            tuple: (bool, float) - (is_valid, actual_duration)
        """
        try:
            audio, sr = torchaudio.load(audio_path)
            duration = audio.shape[1] / sr
            is_valid = duration >= min_duration
            return is_valid, duration
        except Exception as e:
            logger.error(f"Error validating audio duration: {e}")
            return False, 0.0

    def info(self):
        """
        Get information about the voice cloner

        Returns:
            dict: Information dictionary
        """
        return {
            'device': self.device,
            'model': 'Fish Speech S1-mini',
            'supported_languages': len(self.supported_languages),
            'languages': self.supported_languages,
            'checkpoint': str(self.checkpoint_path),
        }


def main():
    """
    Example usage of VoiceCloner with Fish Speech
    """
    # Initialize
    cloner = VoiceCloner()

    # Print info
    info = cloner.info()
    print(f"\n{'='*60}")
    print("Fish Speech Voice Cloner Information")
    print(f"{'='*60}")
    print(f"Device: {info['device']}")
    print(f"Model: {info['model']}")
    print(f"Supported Languages: {info['supported_languages']}")
    print(f"Checkpoint: {info['checkpoint']}")
    print(f"{'='*60}\n")

    # Example usage (if audio files exist)
    speaker_wav = "recordings/my_voice.wav"
    if os.path.exists(speaker_wav):
        text = "Olá, o meu nome é Fernando. Este é um teste do Fish Speech com português de Portugal."
        output = "outputs/fish_test_output.wav"

        try:
            result = cloner.clone_voice(
                text=text,
                speaker_wav=speaker_wav,
                language='pt',
                output_path=output
            )
            print(f"✅ Success! Audio saved to: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("ℹ️  No reference audio found. Please record your voice first.")


if __name__ == "__main__":
    main()

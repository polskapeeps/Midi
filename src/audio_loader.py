"""Audio file loading and validation."""

import librosa
import numpy as np
from pathlib import Path
from typing import Tuple


class AudioLoader:
    """Handles loading and validating audio files."""

    SUPPORTED_FORMATS = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    DEFAULT_SR = 22050  # Sample rate (Hz)
    MAX_DURATION = 600  # 10 minutes in seconds
    MIN_DURATION = 0.5  # 0.5 seconds

    @staticmethod
    def load(file_path: str, sr: int = None) -> Tuple[np.ndarray, int]:
        """
        Load audio file and return waveform + sample rate.

        Args:
            file_path: Path to audio file
            sr: Target sample rate (None = preserve original)

        Returns:
            Tuple of (audio_data, sample_rate)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported or audio invalid
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        if path.suffix.lower() not in AudioLoader.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {path.suffix}. "
                f"Supported: {', '.join(AudioLoader.SUPPORTED_FORMATS)}"
            )

        # Load audio (convert to mono)
        sr = sr or AudioLoader.DEFAULT_SR
        audio, sample_rate = librosa.load(file_path, sr=sr, mono=True)

        # Validate
        AudioLoader.validate(audio, sample_rate)

        return audio, sample_rate

    @staticmethod
    def validate(audio: np.ndarray, sr: int) -> bool:
        """
        Validate audio data is suitable for processing.

        Args:
            audio: Audio waveform
            sr: Sample rate

        Returns:
            True if valid

        Raises:
            ValueError: If audio is invalid
        """
        duration = len(audio) / sr

        if duration < AudioLoader.MIN_DURATION:
            raise ValueError(
                f"Audio too short: {duration:.2f}s (minimum {AudioLoader.MIN_DURATION}s)"
            )

        if duration > AudioLoader.MAX_DURATION:
            raise ValueError(
                f"Audio too long: {duration:.2f}s (maximum {AudioLoader.MAX_DURATION}s)"
            )

        if np.max(np.abs(audio)) < 0.001:
            raise ValueError("Audio appears to be silent (max amplitude < 0.001)")

        return True

    @staticmethod
    def get_duration(audio: np.ndarray, sr: int) -> float:
        """Get audio duration in seconds."""
        return len(audio) / sr

    @staticmethod
    def get_info(file_path: str) -> dict:
        """
        Get audio file information without loading full file.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with format, duration, channels, sample_rate
        """
        path = Path(file_path)

        try:
            # Load just a small portion to get metadata
            info = librosa.get_duration(path=file_path)
            sr = librosa.get_samplerate(path=file_path)

            return {
                'format': path.suffix,
                'duration': info,
                'sample_rate': sr,
                'file_size': path.stat().st_size,
            }
        except Exception as e:
            raise ValueError(f"Failed to read audio info: {e}")


if __name__ == "__main__":
    # Example usage
    loader = AudioLoader()

    # Test with a file
    # audio, sr = loader.load("path/to/stem.wav")
    # print(f"Loaded audio: {len(audio)} samples at {sr} Hz")
    # print(f"Duration: {loader.get_duration(audio, sr):.2f} seconds")

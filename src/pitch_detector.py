"""Pitch detection and note extraction."""

import numpy as np
from typing import Tuple, List, Optional
from pathlib import Path


class PitchDetector:
    """Handles pitch detection using various algorithms."""

    def __init__(self, algorithm: str = "basic-pitch"):
        """
        Initialize pitch detector.

        Args:
            algorithm: Which algorithm to use ("basic-pitch", "crepe", "pyin")
        """
        self.algorithm = algorithm.lower()
        self.model = None

        if self.algorithm == "basic-pitch":
            self._init_basic_pitch()
        elif self.algorithm == "crepe":
            self._init_crepe()
        elif self.algorithm == "pyin":
            self._init_pyin()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def _init_basic_pitch(self):
        """Initialize Basic Pitch model."""
        try:
            from basic_pitch.inference import predict
            from basic_pitch import ICASSP_2022_MODEL_PATH
            self.model = "basic-pitch"
            self._predict_func = predict
        except ImportError:
            raise ImportError(
                "basic-pitch not installed. Run: pip install basic-pitch"
            )

    def _init_crepe(self):
        """Initialize CREPE model (for future implementation)."""
        raise NotImplementedError("CREPE support coming soon")

    def _init_pyin(self):
        """Initialize pYIN algorithm (for future implementation)."""
        raise NotImplementedError("pYIN support coming soon")

    def detect(self, audio_path: str) -> Tuple[np.ndarray, List[dict], dict]:
        """
        Detect pitches from audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of:
            - model_output: Raw model predictions
            - note_events: List of detected notes with timing/pitch/velocity
            - metadata: Additional info (confidence scores, etc.)
        """
        if self.algorithm == "basic-pitch":
            return self._detect_basic_pitch(audio_path)
        else:
            raise NotImplementedError(f"{self.algorithm} not yet implemented")

    def _detect_basic_pitch(self, audio_path: str) -> Tuple:
        """
        Run Basic Pitch inference.

        Returns:
            Tuple of (model_output, note_events, metadata)
        """
        from basic_pitch.inference import predict

        # Run prediction
        model_output, midi_data, note_events = predict(audio_path)

        # Convert note_events to more usable format
        notes = []
        for start_time, end_time, pitch, velocity, pitch_bends in note_events:
            notes.append({
                'start_time': float(start_time),
                'end_time': float(end_time),
                'duration': float(end_time - start_time),
                'pitch': int(pitch),
                'velocity': float(velocity),
                'note_name': self._midi_to_note_name(int(pitch)),
                'confidence': float(velocity),  # Basic Pitch uses velocity as confidence
                'pitch_bends': pitch_bends if pitch_bends else []
            })

        # Metadata
        metadata = {
            'algorithm': 'basic-pitch',
            'num_notes': len(notes),
            'duration': max(n['end_time'] for n in notes) if notes else 0,
            'pitch_range': (
                min(n['pitch'] for n in notes),
                max(n['pitch'] for n in notes)
            ) if notes else (0, 0)
        }

        return model_output, notes, metadata

    @staticmethod
    def _midi_to_note_name(midi_pitch: int) -> str:
        """Convert MIDI pitch number to note name (e.g., 60 -> 'C4')."""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi_pitch // 12) - 1
        note = note_names[midi_pitch % 12]
        return f"{note}{octave}"

    def filter_notes(
        self,
        notes: List[dict],
        min_confidence: float = 0.3,
        min_duration: float = 0.05
    ) -> List[dict]:
        """
        Filter out low-confidence or very short notes.

        Args:
            notes: List of note dictionaries
            min_confidence: Minimum confidence threshold (0-1)
            min_duration: Minimum note duration in seconds

        Returns:
            Filtered list of notes
        """
        filtered = [
            note for note in notes
            if note['confidence'] >= min_confidence
            and note['duration'] >= min_duration
        ]

        return filtered

    def quantize_timing(
        self,
        notes: List[dict],
        grid: float = 0.125,  # 16th note at 120 BPM
        strength: float = 0.8  # 0-1, how much to quantize
    ) -> List[dict]:
        """
        Quantize note timings to rhythmic grid.

        Args:
            notes: List of note dictionaries
            grid: Grid size in seconds
            strength: Quantization strength (0 = none, 1 = full)

        Returns:
            Notes with quantized timings
        """
        quantized = []

        for note in notes:
            quantized_note = note.copy()

            # Quantize start time
            start = note['start_time']
            grid_pos = round(start / grid) * grid
            quantized_note['start_time'] = start + (grid_pos - start) * strength

            # Quantize end time
            end = note['end_time']
            grid_pos = round(end / grid) * grid
            quantized_note['end_time'] = end + (grid_pos - end) * strength

            # Update duration
            quantized_note['duration'] = (
                quantized_note['end_time'] - quantized_note['start_time']
            )

            quantized.append(quantized_note)

        return quantized


if __name__ == "__main__":
    # Example usage
    detector = PitchDetector(algorithm="basic-pitch")

    # Test with a file
    # output, notes, metadata = detector.detect("path/to/stem.wav")
    # print(f"Detected {len(notes)} notes")
    # print(f"Pitch range: {metadata['pitch_range']}")

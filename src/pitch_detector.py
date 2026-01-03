"""Pitch detection and note extraction."""

import numpy as np
from typing import Tuple, List


class PitchDetector:
    """Handles pitch detection using various algorithms."""

    DRUM_MIDI_MAP = {
        "kick": 36,   # C1
        "snare": 38,  # D1
        "hat": 42,    # F#1 (closed hat)
    }

    def __init__(self, algorithm: str = "pyin", lazy_init: bool = False):
        """
        Initialize pitch detector.

        Args:
            algorithm: Which algorithm to use ("basic-pitch", "pyin")
            lazy_init: Delay heavy model loading until detection
        """
        self.algorithm = algorithm.lower()
        self.model = None
        self._predict_func = None
        self._initialized = False

        if self.algorithm not in {"basic-pitch", "pyin", "drums"}:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        if not lazy_init:
            self._initialize_model()

    def _initialize_model(self):
        """Initialize the requested algorithm if not already loaded."""
        if self._initialized:
            return

        if self.algorithm == "basic-pitch":
            self._init_basic_pitch()
        elif self.algorithm == "pyin":
            self._init_pyin()
        elif self.algorithm == "drums":
            self._init_drums()

        self._initialized = True

    def _init_basic_pitch(self):
        """Initialize Basic Pitch model."""
        try:
            from basic_pitch.inference import predict
            from basic_pitch import ICASSP_2022_MODEL_PATH
            self.model = "basic-pitch"
            self._predict_func = predict
        except ImportError:
            raise ImportError(
                "basic-pitch not installed or incompatible with this Python version. "
                "Install with Python 3.11 (TensorFlow-supported) using: pip install basic-pitch"
            )

    def _init_pyin(self):
        """Initialize pYIN configuration (librosa-based)."""
        try:
            import librosa  # noqa: F401
        except ImportError:
            raise ImportError("librosa is required for the pYIN algorithm. Install via pip install librosa")

        self.model = "pyin"
        self._pyin_config = {
            "frame_length": 2048,
            "hop_length": 512,
            "fmin": "C2",
            "fmax": "C7",
        }

    def _init_drums(self):
        """Initialize drum detection configuration (librosa-based)."""
        try:
            import librosa  # noqa: F401
        except ImportError:
            raise ImportError("librosa is required for the drums algorithm. Install via pip install librosa")

        self.model = "drums"
        self._drums_config = {
            "sr": 22050,
            "hop_length": 512,
            "n_fft": 2048,
            "min_duration": 0.08,
        }

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
        if not self._initialized:
            self._initialize_model()

        if self.algorithm == "basic-pitch":
            return self._detect_basic_pitch(audio_path)
        if self.algorithm == "pyin":
            return self._detect_pyin(audio_path)
        if self.algorithm == "drums":
            return self._detect_drums(audio_path)

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

    def _detect_pyin(self, audio_path: str) -> Tuple:
        """
        Run monophonic pYIN pitch tracking via librosa.

        Returns:
            Tuple of (model_output, note_events, metadata)
        """
        import librosa

        hop_length = self._pyin_config["hop_length"]
        frame_length = self._pyin_config["frame_length"]
        fmin_hz = librosa.note_to_hz(self._pyin_config["fmin"])
        fmax_hz = librosa.note_to_hz(self._pyin_config["fmax"])

        audio, sr = librosa.load(audio_path, sr=None, mono=True)

        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=fmin_hz,
            fmax=fmax_hz,
            sr=sr,
            frame_length=frame_length,
            hop_length=hop_length,
        )

        times = librosa.times_like(f0, sr=sr, hop_length=hop_length)
        frame_duration = hop_length / sr

        notes = []
        current_note = None

        for time, pitch_hz, prob in zip(times, f0, voiced_probs):
            if np.isnan(pitch_hz):
                if current_note:
                    self._close_note(current_note, time, frame_duration, notes)
                    current_note = None
                continue

            midi_pitch = int(round(librosa.hz_to_midi(pitch_hz)))

            if current_note and current_note["pitch"] == midi_pitch:
                current_note["last_time"] = time
                current_note["confidences"].append(float(prob))
            else:
                if current_note:
                    self._close_note(current_note, time, frame_duration, notes)

                current_note = {
                    "pitch": midi_pitch,
                    "start_time": float(time),
                    "last_time": float(time),
                    "confidences": [float(prob)],
                }

        if current_note:
            self._close_note(current_note, times[-1] + frame_duration, frame_duration, notes)

        metadata = {
            "algorithm": "pyin",
            "num_notes": len(notes),
            "duration": float(len(audio) / sr),
            "pitch_range": (
                min(n["pitch"] for n in notes),
                max(n["pitch"] for n in notes),
            ) if notes else (0, 0),
        }

        return np.array(f0), notes, metadata

    def _detect_drums(self, audio_path: str) -> Tuple:
        """
        Detect drum hits using onset detection and band energy heuristics.

        Returns:
            Tuple of (model_output, note_events, metadata)
        """
        import librosa

        sr = self._drums_config["sr"]
        hop_length = self._drums_config["hop_length"]
        n_fft = self._drums_config["n_fft"]
        min_duration = self._drums_config["min_duration"]

        audio, _ = librosa.load(audio_path, sr=sr, mono=True)

        onset_env = librosa.onset.onset_strength(y=audio, sr=sr, hop_length=hop_length)
        onset_frames = self._pick_onsets(onset_env, sr=sr, hop_length=hop_length)

        if len(onset_frames) == 0:
            metadata = {
                "algorithm": "drums",
                "num_notes": 0,
                "duration": 0,
                "pitch_range": (0, 0),
            }
            return onset_env, [], metadata

        spectrum = np.abs(librosa.stft(audio, n_fft=n_fft, hop_length=hop_length))
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

        kick_band = (20, 120)
        snare_band = (120, 2500)
        hat_band = (2500, 10000)

        kick_idx = np.where((freqs >= kick_band[0]) & (freqs < kick_band[1]))[0]
        snare_idx = np.where((freqs >= snare_band[0]) & (freqs < snare_band[1]))[0]
        hat_idx = np.where((freqs >= hat_band[0]) & (freqs < hat_band[1]))[0]

        max_onset = float(np.max(onset_env)) if len(onset_env) else 1.0

        notes = []
        for frame in onset_frames:
            if frame >= spectrum.shape[1]:
                continue

            mag = spectrum[:, frame]
            total = float(np.sum(mag))
            if total <= 0:
                continue

            kick_energy = float(np.sum(mag[kick_idx]))
            snare_energy = float(np.sum(mag[snare_idx]))
            hat_energy = float(np.sum(mag[hat_idx]))

            energies = {
                "kick": kick_energy,
                "snare": snare_energy,
                "hat": hat_energy,
            }
            label = max(energies, key=energies.get)

            onset_time = float(librosa.frames_to_time(frame, sr=sr, hop_length=hop_length))
            velocity = float(min(1.0, max(0.0, onset_env[frame] / max_onset)))

            notes.append({
                "start_time": onset_time,
                "end_time": onset_time + min_duration,
                "duration": min_duration,
                "pitch": self.DRUM_MIDI_MAP[label],
                "velocity": velocity,
                "note_name": label,
                "confidence": velocity,
                "pitch_bends": [],
            })

        metadata = {
            "algorithm": "drums",
            "num_notes": len(notes),
            "duration": max((n["end_time"] for n in notes), default=0),
            "pitch_range": (
                min((n["pitch"] for n in notes), default=0),
                max((n["pitch"] for n in notes), default=0),
            ),
        }

        return onset_env, notes, metadata

    def _close_note(self, current_note: dict, end_time: float, frame_duration: float, notes: List[dict]):
        """Finalize a note and append to the notes list."""
        duration = max(frame_duration, end_time - current_note["start_time"])
        confidence = float(np.mean(current_note["confidences"])) if current_note["confidences"] else 0.0

        notes.append({
            "start_time": float(current_note["start_time"]),
            "end_time": float(end_time),
            "duration": float(duration),
            "pitch": int(current_note["pitch"]),
            "velocity": float(min(1.0, max(0.0, confidence))),
            "note_name": self._midi_to_note_name(int(current_note["pitch"])),
            "confidence": confidence,
            "pitch_bends": [],
        })

    @staticmethod
    def _pick_onsets(onset_env: np.ndarray, sr: int, hop_length: int) -> np.ndarray:
        """Pick onset frames using a simple peak-picking heuristic."""
        if onset_env.size < 3:
            return np.array([], dtype=int)

        threshold = float(np.median(onset_env) + 0.5 * np.std(onset_env))
        min_interval = max(1, int(0.05 * sr / hop_length))

        peaks = []
        for i in range(1, len(onset_env) - 1):
            if onset_env[i] < threshold:
                continue
            if onset_env[i] >= onset_env[i - 1] and onset_env[i] >= onset_env[i + 1]:
                if peaks and (i - peaks[-1]) < min_interval:
                    continue
                peaks.append(i)

        return np.array(peaks, dtype=int)

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
        tempo: int = 120,
        subdivision: int = 4,
        strength: float = 0.8  # 0-1, how much to quantize
    ) -> List[dict]:
        """
        Quantize note timings to rhythmic grid.

        Args:
            notes: List of note dictionaries
            tempo: Tempo in BPM used to derive grid size
            subdivision: Number of sub-beats per beat (4 = 16th notes)
            strength: Quantization strength (0 = none, 1 = full)

        Returns:
            Notes with quantized timings
        """
        if tempo <= 0:
            raise ValueError("Tempo must be positive")
        if subdivision <= 0:
            raise ValueError("Subdivision must be positive")

        seconds_per_beat = 60.0 / tempo
        grid = seconds_per_beat / subdivision
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
    detector = PitchDetector(algorithm="pyin")

    # Test with a file
    # output, notes, metadata = detector.detect("path/to/stem.wav")
    # print(f"Detected {len(notes)} notes")
    # print(f"Pitch range: {metadata['pitch_range']}")

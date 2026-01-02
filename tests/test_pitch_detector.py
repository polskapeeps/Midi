import sys
from pathlib import Path
import unittest

# Ensure src is importable
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from pitch_detector import PitchDetector  # noqa: E402


class TestPitchDetectorQuantize(unittest.TestCase):
    def test_quantize_respects_tempo_and_subdivision(self):
        detector = PitchDetector(lazy_init=True)

        notes = [
            {"start_time": 0.11, "end_time": 0.36, "duration": 0.25, "pitch": 60, "velocity": 0.8, "confidence": 0.9},
            {"start_time": 0.61, "end_time": 0.86, "duration": 0.25, "pitch": 64, "velocity": 0.7, "confidence": 0.8},
        ]

        # 100 BPM, 8th note grid -> grid = (60/100)/2 = 0.3s
        quantized = detector.quantize_timing(notes, tempo=100, subdivision=2, strength=1.0)

        self.assertAlmostEqual(quantized[0]["start_time"], 0.0, places=3)
        self.assertAlmostEqual(quantized[0]["end_time"], 0.3, places=3)
        self.assertAlmostEqual(quantized[1]["start_time"], 0.6, places=3)
        self.assertAlmostEqual(quantized[1]["end_time"], 0.9, places=3)

    def test_quantize_invalid_inputs(self):
        detector = PitchDetector(lazy_init=True)
        with self.assertRaises(ValueError):
            detector.quantize_timing([], tempo=0)
        with self.assertRaises(ValueError):
            detector.quantize_timing([], tempo=120, subdivision=0)


if __name__ == "__main__":
    unittest.main()

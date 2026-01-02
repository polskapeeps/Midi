import sys
from pathlib import Path
import tempfile
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from midi_exporter import MidiExporter  # noqa: E402


class TestMidiExporter(unittest.TestCase):
    def test_exports_midi_file(self):
        exporter = MidiExporter(tempo=120, ticks_per_beat=480)
        notes = [
            {"start_time": 0.0, "end_time": 0.5, "duration": 0.5, "pitch": 60, "velocity": 0.8},
            {"start_time": 0.5, "end_time": 1.0, "duration": 0.5, "pitch": 64, "velocity": 0.7},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.mid"
            saved = exporter.export(notes, str(output_path), track_name="Test")
            self.assertTrue(Path(saved).exists())


if __name__ == "__main__":
    unittest.main()

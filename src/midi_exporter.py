"""MIDI file export functionality."""

import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
from typing import List, Optional
from pathlib import Path


class MidiExporter:
    """Handles exporting note data to MIDI files."""

    DEFAULT_TEMPO = 120  # BPM
    DEFAULT_TICKS_PER_BEAT = 480
    DEFAULT_PROGRAM = 0  # Acoustic Grand Piano

    def __init__(
        self,
        tempo: int = DEFAULT_TEMPO,
        ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT,
        program: int = DEFAULT_PROGRAM
    ):
        """
        Initialize MIDI exporter.

        Args:
            tempo: Tempo in BPM
            ticks_per_beat: MIDI ticks per quarter note
            program: MIDI program number (0-127)
        """
        self.tempo = tempo
        self.ticks_per_beat = ticks_per_beat
        self.program = program

    def export(
        self,
        notes: List[dict],
        output_path: str,
        track_name: str = "Converted Audio"
    ) -> str:
        """
        Export notes to MIDI file.

        Args:
            notes: List of note dictionaries with start_time, end_time, pitch, velocity
            output_path: Where to save MIDI file
            track_name: Name for the MIDI track

        Returns:
            Path to saved MIDI file
        """
        if not notes:
            raise ValueError("No notes to export")

        # Create MIDI file
        mid = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)

        # Add track name
        track.append(MetaMessage('track_name', name=track_name, time=0))

        # Add tempo
        tempo_microseconds = mido.bpm2tempo(self.tempo)
        track.append(MetaMessage('set_tempo', tempo=tempo_microseconds, time=0))

        # Add program change (instrument)
        track.append(Message('program_change', program=self.program, time=0))

        # Sort notes by start time
        sorted_notes = sorted(notes, key=lambda n: n['start_time'])

        # Convert notes to MIDI messages
        events = []
        for note in sorted_notes:
            # Note on event
            events.append({
                'time': note['start_time'],
                'type': 'note_on',
                'pitch': int(note['pitch']),
                'velocity': int(note.get('velocity', 0.8) * 127)
            })

            # Note off event
            events.append({
                'time': note['end_time'],
                'type': 'note_off',
                'pitch': int(note['pitch']),
                'velocity': 0
            })

        # Sort all events by time
        events.sort(key=lambda e: e['time'])

        # Convert absolute times to delta times
        current_time = 0
        for event in events:
            absolute_time = event['time']
            delta_time = absolute_time - current_time
            delta_ticks = self._seconds_to_ticks(delta_time)

            if event['type'] == 'note_on':
                track.append(Message(
                    'note_on',
                    note=event['pitch'],
                    velocity=event['velocity'],
                    time=delta_ticks
                ))
            elif event['type'] == 'note_off':
                track.append(Message(
                    'note_off',
                    note=event['pitch'],
                    velocity=0,
                    time=delta_ticks
                ))

            current_time = absolute_time

        # Add end of track
        track.append(MetaMessage('end_of_track', time=0))

        # Save file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mid.save(output_path)

        return str(output_path)

    def _seconds_to_ticks(self, seconds: float) -> int:
        """Convert time in seconds to MIDI ticks."""
        # seconds per beat = 60 / BPM
        seconds_per_beat = 60.0 / self.tempo
        beats = seconds / seconds_per_beat
        ticks = int(beats * self.ticks_per_beat)
        return max(0, ticks)  # Ensure non-negative

    def set_tempo(self, tempo: int):
        """Set tempo in BPM."""
        if tempo < 20 or tempo > 400:
            raise ValueError("Tempo must be between 20 and 400 BPM")
        self.tempo = tempo

    def set_program(self, program: int):
        """Set MIDI program (instrument) number."""
        if program < 0 or program > 127:
            raise ValueError("Program must be between 0 and 127")
        self.program = program

    @staticmethod
    def get_program_name(program: int) -> str:
        """Get instrument name for MIDI program number."""
        # Simplified list of common instruments
        programs = {
            0: "Acoustic Grand Piano",
            1: "Bright Acoustic Piano",
            24: "Acoustic Guitar (nylon)",
            25: "Acoustic Guitar (steel)",
            32: "Acoustic Bass",
            33: "Electric Bass (finger)",
            40: "Violin",
            48: "String Ensemble 1",
            73: "Flute",
            # Add more as needed
        }
        return programs.get(program, f"Program {program}")


if __name__ == "__main__":
    # Example usage
    exporter = MidiExporter(tempo=120)

    # Example notes
    example_notes = [
        {'start_time': 0.0, 'end_time': 0.5, 'pitch': 60, 'velocity': 0.8},
        {'start_time': 0.5, 'end_time': 1.0, 'pitch': 64, 'velocity': 0.7},
        {'start_time': 1.0, 'end_time': 1.5, 'pitch': 67, 'velocity': 0.9},
    ]

    # Export
    # exporter.export(example_notes, "output/test.mid", track_name="Test Track")
    # print("MIDI file saved!")

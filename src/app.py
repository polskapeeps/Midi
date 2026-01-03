#!/usr/bin/env python3
"""
Audio to MIDI Extraction - Main Application

CLI tool to convert audio stems to MIDI files.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from audio_loader import AudioLoader
from pitch_detector import PitchDetector
from midi_exporter import MidiExporter


class AudioToMidiApp:
    """Main application class."""

    def __init__(
        self,
        algorithm: str = "pyin",
        tempo: int = 120,
        min_confidence: float = 0.3,
        min_duration: float = 0.05
    ):
        """
        Initialize application.

        Args:
            algorithm: Pitch detection algorithm to use
            tempo: MIDI tempo in BPM
            min_confidence: Minimum note confidence threshold
            min_duration: Minimum note duration in seconds
        """
        self.loader = AudioLoader()
        self.detector = PitchDetector(algorithm=algorithm)
        self.exporter = MidiExporter(tempo=tempo)
        self.min_confidence = min_confidence
        self.min_duration = min_duration

    def process(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        quantize: bool = False,
        verbose: bool = True
    ) -> str:
        """
        Convert audio file to MIDI.

        Args:
            input_path: Path to audio file
            output_path: Path for output MIDI (auto-generated if None)
            quantize: Whether to quantize note timings
            verbose: Print progress messages

        Returns:
            Path to output MIDI file
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Auto-generate output path if not provided
        if output_path is None:
            output_path = input_path.with_suffix('.mid')

        if verbose:
            print("Audio to MIDI Conversion")
            print(f"{'='*50}")
            print(f"Input:  {input_path}")
            print(f"Output: {output_path}")
            print()

        # Step 1: Load audio
        if verbose:
            print("Loading audio file...")

        audio, sr = self.loader.load(str(input_path))
        duration = self.loader.get_duration(audio, sr)

        if verbose:
            print(f"   OK Loaded {duration:.2f} seconds at {sr} Hz")
            print()

        # Step 2: Detect pitches
        if verbose:
            print("Detecting notes (this may take 10-30 seconds)...")

        model_output, notes, metadata = self.detector.detect(str(input_path))

        if verbose:
            print(f"   OK Found {len(notes)} raw notes")
            if notes:
                pitch_min, pitch_max = metadata['pitch_range']
                print(f"   OK Pitch range: {self.detector._midi_to_note_name(pitch_min)} "
                      f"to {self.detector._midi_to_note_name(pitch_max)}")
            print()

        # Step 3: Filter notes
        if verbose:
            print(f"Filtering notes (confidence >= {self.min_confidence}, "
                  f"duration >= {self.min_duration}s)...")

        filtered_notes = self.detector.filter_notes(
            notes,
            min_confidence=self.min_confidence,
            min_duration=self.min_duration
        )

        if verbose:
            removed = len(notes) - len(filtered_notes)
            print(f"   OK Kept {len(filtered_notes)} notes (removed {removed})")
            print()

        # Step 4: Quantize if requested
        if quantize:
            if verbose:
                print("Quantizing note timings...")
            filtered_notes = self.detector.quantize_timing(
                filtered_notes,
                tempo=self.exporter.tempo,
                subdivision=4,
                strength=0.9,
            )
            if verbose:
                print("   OK Notes quantized to grid")
                print()

        # Step 5: Export MIDI
        if verbose:
            print("Exporting MIDI file...")

        if not filtered_notes:
            print("   WARNING: No notes to export!")
            return None

        track_name = input_path.stem
        channel = 9 if self.detector.algorithm == "drums" else 0
        program = None if self.detector.algorithm == "drums" else self.exporter.program
        output_file = self.exporter.export(
            filtered_notes,
            str(output_path),
            track_name=track_name,
            channel=channel,
            program=program,
        )

        if verbose:
            print(f"   OK Saved: {output_file}")
            print()
            print("Conversion complete!")
            print("\nSummary:")
            print(f"   - Input duration: {duration:.2f}s")
            print(f"   - Notes exported: {len(filtered_notes)}")
            print(f"   - Algorithm: {metadata['algorithm']}")

        return output_file


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert audio stems to MIDI files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a bass stem to MIDI
  python app.py bass_stem.wav

  # Specify output path and tempo
  python app.py piano.wav -o output.mid -t 140

  # Use quantization and higher confidence threshold
  python app.py vocal.wav -q -c 0.5

Supported audio formats:
  WAV, MP3, FLAC, OGG, M4A
        """
    )

    parser.add_argument(
        'input',
        help='Input audio file (stem, not full mix)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output MIDI file (default: same name as input with .mid extension)'
    )

    parser.add_argument(
        '-a', '--algorithm',
        choices=['basic-pitch', 'pyin', 'drums'],
        default='pyin',
        help='Algorithm (pyin for melodic, drums for drum hits; basic-pitch on Python 3.11)'
    )

    parser.add_argument(
        '-t', '--tempo',
        type=int,
        default=120,
        help='MIDI tempo in BPM (default: 120)'
    )

    parser.add_argument(
        '-c', '--confidence',
        type=float,
        default=0.3,
        help='Minimum note confidence threshold 0-1 (default: 0.3)'
    )

    parser.add_argument(
        '-d', '--min-duration',
        type=float,
        default=0.05,
        help='Minimum note duration in seconds (default: 0.05)'
    )

    parser.add_argument(
        '-q', '--quantize',
        action='store_true',
        help='Quantize note timings to rhythmic grid'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )

    args = parser.parse_args()

    try:
        # Create app
        app = AudioToMidiApp(
            algorithm=args.algorithm,
            tempo=args.tempo,
            min_confidence=args.confidence,
            min_duration=args.min_duration
        )

        # Process file
        output_path = app.process(
            input_path=args.input,
            output_path=args.output,
            quantize=args.quantize,
            verbose=not args.quiet
        )

        if output_path:
            sys.exit(0)
        else:
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

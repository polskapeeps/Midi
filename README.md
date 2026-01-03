# Audio to MIDI Extraction App

Convert pre-separated audio stems into MIDI files with high accuracy.

## Overview

This application focuses on converting **already-separated audio stems** (bass, piano, vocals, guitar, etc.) into clean MIDI files. By processing individual stems rather than full mixes, we achieve:

- ⚡ **10x faster processing** (10-30 seconds vs. 2-5 minutes)
- 🎯 **Higher accuracy** (85-95% for monophonic, 70-80% for polyphonic)
- 💻 **Lower system requirements** (no GPU needed)
- 🎛️ **Better control** (use your DAW's stem separation tools)

## Features

- **Load audio stems** (WAV, MP3, FLAC)
- **Pitch detection**
  - ✅ **pYIN (librosa)** monophonic tracker (default, works on Python 3.12+)
  - ✅ **Basic Pitch** support (best quality, requires Python 3.11 + TensorFlow)
  - ?o. **Drums** onset-based detection for kick/snare/hat (fast heuristic)
- **Tempo-aware quantization** to tighten detected notes
- **Export to MIDI** (.mid files for any DAW)

Note: Drum detection is heuristic and works best on isolated drum stems.

Planned next (from DESIGN.md): waveform/piano-roll visualization and in-app MIDI editing.

## Quick Start

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Midi

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies (pyin pipeline, works on Python 3.12+)
pip install -r requirements.txt

# Optional: install Basic Pitch for higher accuracy (requires Python 3.11)
# pip install basic-pitch
```

### Basic Usage

```bash
# Convert a stem using the default pYIN pipeline
python src/app.py path/to/stem.wav

# Run with Basic Pitch (requires Python 3.11 + TensorFlow)
python src/app.py path/to/stem.wav --algorithm basic-pitch

# Quick drum MIDI (kick/snare/hat) from a drum stem
python src/app.py path/to/drums.wav --algorithm drums --quantize
# Output uses GM drum channel (10)

# Enable quantization and custom tempo
python src/app.py path/to/stem.wav --quantize --tempo 140
```

### GUI Preview (PyQt6)

The first-pass GUI wraps the existing CLI pipeline. Launch it after installing
PyQt6:

```bash
pip install -r requirements.txt  # ensure PyQt6 is available
python -m ui.main_window
```

Use the controls to select an input stem, optionally adjust algorithm/tempo/
thresholds, and start the conversion without leaving the app. The layout is
kept simple so we can iterate on optional features (visualization, batch
queues, MIDI editing) in future updates.

## Project Status

🚧 **In Development** - See [DESIGN.md](DESIGN.md) for full design concept

- [x] Design document completed
- [x] Project structure created
- [x] Core audio processing pipeline (pYIN + Basic Pitch optional)
- [x] CLI interface with quantization
- [ ] GUI application (PyQt6) — initial layout implemented for preview
- [ ] MIDI editing tools
- [ ] Package for distribution

## Technology

- **Python**: pYIN works on 3.12+; Basic Pitch requires 3.11
- **Basic Pitch** (Spotify's ML pitch detector)
- **librosa** (audio analysis / pYIN)
- **mido** (MIDI creation)
- **PyQt6** (desktop GUI)

## Documentation

- [Design Document](DESIGN.md) - Complete technical design and analysis
- [Getting Started Guide](GETTING_STARTED.md) - How to begin development
- [User Guide](docs/user_guide.md) - How to use the application (coming soon)

## License

TBD

## Contributing

This project is currently in early development. Contributions welcome once MVP is complete.

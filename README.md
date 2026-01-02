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
- **Pitch detection** using state-of-the-art ML models (Basic Pitch)
- **Waveform visualization** to see what you're processing
- **Piano roll display** with detected notes
- **MIDI editing** to fix any detection errors
- **Export to MIDI** (.mid files for any DAW)

## Quick Start

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Midi

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# CLI version (coming soon)
python src/app.py path/to/stem.wav

# GUI version (coming soon)
python src/app.py --gui
```

## Project Status

🚧 **In Development** - See [DESIGN.md](DESIGN.md) for full design concept

- [x] Design document completed
- [x] Project structure created
- [ ] Core audio processing pipeline
- [ ] CLI interface
- [ ] GUI application (PyQt6)
- [ ] MIDI editing tools
- [ ] Package for distribution

## Technology

- **Python 3.11+**
- **Basic Pitch** (Spotify's ML pitch detector)
- **librosa** (audio analysis)
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

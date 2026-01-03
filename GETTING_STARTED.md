# Getting Started - Audio to MIDI Extraction App

## Your Simplified Approach

**Smart Decision**: By focusing on **pre-separated stems** rather than doing full separation in-app, you're:
- ✅ Reducing computational requirements by 80%+
- ✅ Skipping the slowest processing step (2-5 min → ~10 sec)
- ✅ Letting users leverage their DAW's built-in stem separation
- ✅ Focusing on what matters: **high-quality MIDI conversion**

## Revised MVP Scope

Instead of the full pipeline, focus on:

```
Separated Stem (WAV/MP3) → Pitch Detection → MIDI Export
     ↓
  [Your App]
     ↓
  Clean MIDI file
```

### Core Features (Simplified MVP)
1. **Load audio file** (WAV, MP3) - individual stem, not full mix
2. **Waveform visualization** - see what you're processing
3. **Pitch detection** - with multiple algorithm options
4. **Piano roll display** - visualize detected notes
5. **Manual editing** - fix errors quickly
6. **MIDI export** - save to .mid file

**Processing time**: ~10-30 seconds per stem (vs. 2-5 minutes for full separation)

---

## How to Begin: 3 Options

### Option A: Quick Python Prototype (Recommended) ⭐

**Time**: 1-2 days for working MVP
**Best for**: Rapid iteration, testing with real audio

**Stack**:
- Python 3.11+
- `basic-pitch` (Spotify's ML pitch detector)
- `librosa` (audio analysis)
- `mido` (MIDI export)
- `matplotlib` or `pyqtgraph` (visualization)
- `PyQt6` or `tkinter` (GUI - can start with CLI)

**Pros**:
- Fastest to working prototype
- Rich ecosystem for audio/ML
- Easy to experiment with different algorithms

**Cons**:
- Slower runtime than compiled languages
- Larger distribution size

---

### Option B: Web Application

**Time**: 2-3 days for working MVP
**Best for**: Cross-platform, modern UI, easy sharing

**Stack**:
- **Frontend**: React/Svelte + TailwindCSS
- **Audio**: Tone.js, WaveSurfer.js
- **Processing**: Python backend (FastAPI) or Node.js + Python microservice
- **Deployment**: Can run locally or host

**Pros**:
- Beautiful, modern UI out of the box
- Works on any platform (macOS, Windows, Linux, even mobile)
- Easy to share with others

**Cons**:
- More complex architecture
- Need to handle file uploads
- May need backend for heavy processing

---

### Option C: Start with CLI, Add GUI Later

**Time**: 3-6 hours for CLI, +1-2 days for GUI
**Best for**: Testing algorithms first, UI polish later

**Stack**:
- Python CLI using `click` or `argparse`
- Add PyQt6 GUI when ready

**Pros**:
- Fastest to test core functionality
- Forces focus on algorithm quality
- Can use CLI for batch processing

**Cons**:
- Less impressive for demos
- Need to build UI later anyway

---

## Recommended Start: Option A (Python Desktop App)

Here's the step-by-step plan:

### Phase 1: Core Functionality (Day 1)
```python
# What you'll build:
1. Load audio file (WAV)
2. Run Basic Pitch on it
3. Save MIDI file
4. Print results to console
```

**Result**: Working CLI that converts stem → MIDI

### Phase 2: Visualization (Day 2)
```python
# Add:
1. Waveform display (matplotlib)
2. Piano roll visualization
3. Show confidence scores
```

**Result**: Can see what's being detected

### Phase 3: GUI (Days 3-4)
```python
# Add:
1. PyQt6 window with buttons
2. File browser
3. Play audio preview
4. Visual MIDI editor
```

**Result**: Usable desktop application

### Phase 4: Refinement (Days 5-7)
```python
# Polish:
1. Add algorithm options (Basic Pitch vs. Crepe vs. pYIN)
2. Note editing tools
3. Export options
4. Settings panel
```

**Result**: Production-ready MVP

---

## Initial Setup (Choose This Path)

### Step 1: Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

Notes:
- Use Python 3.11 if you need Basic Pitch.
- For pYIN only, Python 3.12+ is fine.
- On Windows with multiple versions: `py -3.11 -m venv .venv`

### Step 2: Install Core Dependencies

```bash
# Install core dependencies (pYIN pipeline)
pip install -r requirements.txt

# Optional: Basic Pitch (Python 3.11 only)
# pip install basic-pitch
```

### Step 3: Test with Real Audio

```bash
# Download a test stem or use your own
# Run the app with pYIN (works on Python 3.12+)
python src/app.py path/to/your/stem.wav --algorithm pyin

# Drum MIDI from a drum stem (kick/snare/hat)
python src/app.py path/to/drums.wav --algorithm drums --quantize

# If using Python 3.11 with Basic Pitch installed
# python src/app.py path/to/your/stem.wav --algorithm basic-pitch
```

**If this works**, you've validated the core technology! Everything else is UI/UX.

---

## Project Structure

```
Midi/
├── README.md                 # Project overview
├── DESIGN.md                 # Full design doc (already created)
├── GETTING_STARTED.md        # This file
├── requirements.txt          # Python dependencies
├── setup.py                  # Package config (optional)
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── audio_loader.py       # Load/validate audio files
│   ├── pitch_detector.py     # Pitch detection (Basic Pitch, Crepe, etc.)
│   ├── midi_exporter.py      # MIDI file creation
│   ├── visualizer.py         # Waveform/piano roll display
│   └── app.py                # Main application entry point
│
├── tests/                    # Unit tests
│   ├── test_audio_loader.py
│   ├── test_pitch_detector.py
│   └── test_midi_exporter.py
│
├── ui/                       # GUI code (PyQt6)
│   ├── __init__.py
│   ├── main_window.py        # Main window
│   ├── piano_roll.py         # Piano roll widget
│   └── waveform.py           # Waveform widget
│
├── examples/                 # Sample files for testing
│   ├── bass_stem.wav
│   ├── piano_stem.wav
│   └── vocal_stem.wav
│
└── docs/                     # Documentation
    ├── user_guide.md
    └── api_reference.md
```

---

## Your First Task: Build CLI MVP

**Goal**: Load stem, convert to MIDI, save file (30-60 min)

### Step 1: Create `src/audio_loader.py`

```python
import librosa
import numpy as np

def load_audio(file_path: str, sr: int = 22050):
    """Load audio file and return waveform + sample rate."""
    audio, sample_rate = librosa.load(file_path, sr=sr, mono=True)
    return audio, sample_rate

def validate_audio(audio: np.ndarray, sr: int):
    """Check if audio is valid for processing."""
    duration = len(audio) / sr
    if duration < 0.5:
        raise ValueError("Audio too short (< 0.5s)")
    if duration > 600:  # 10 minutes
        raise ValueError("Audio too long (> 10 min)")
    return True
```

### Step 2: Create `src/pitch_detector.py`

```python
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

def detect_notes(audio_path: str):
    """
    Run Basic Pitch on audio file.
    Returns: (model_output, midi_data, note_events)
    """
    model_output, midi_data, note_events = predict(audio_path)
    return model_output, midi_data, note_events
```

### Step 3: Create `src/midi_exporter.py`

```python
import mido
from mido import MidiFile, MidiTrack, Message

def save_midi(note_events, output_path: str, tempo: int = 120):
    """Save note events to MIDI file."""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Add tempo
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))

    # Convert note events to MIDI messages
    for start_time, end_time, pitch, velocity, _ in note_events:
        # Convert to ticks (assuming 480 ticks per beat)
        start_tick = int(start_time * 480 * (tempo / 60))
        duration_tick = int((end_time - start_time) * 480 * (tempo / 60))

        track.append(Message('note_on', note=pitch, velocity=int(velocity * 127), time=start_tick))
        track.append(Message('note_off', note=pitch, velocity=0, time=duration_tick))

    mid.save(output_path)
    return output_path
```

### Step 4: Create `src/app.py` (CLI version)

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
from audio_loader import load_audio, validate_audio
from pitch_detector import detect_notes
from midi_exporter import save_midi

def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <audio_file.wav>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = Path(input_file).stem + "_converted.mid"

    print(f"Loading audio: {input_file}")
    audio, sr = load_audio(input_file)
    validate_audio(audio, sr)

    print("Detecting notes... (this may take 10-30 seconds)")
    model_output, midi_data, note_events = detect_notes(input_file)

    print(f"Found {len(note_events)} notes")

    print(f"Saving MIDI: {output_file}")
    save_midi(note_events, output_file)

    print("✅ Conversion complete!")

if __name__ == "__main__":
    main()
```

### Step 5: Test It!

```bash
python src/app.py examples/bass_stem.wav
```

**If this works**, you have a functional audio-to-MIDI converter! 🎉

---

## Next Steps After CLI Works

1. **Add waveform visualization** (matplotlib)
2. **Add piano roll display** (matplotlib scatter plot)
3. **Create PyQt6 GUI** (file picker, play button, visual editor)
4. **Add algorithm options** (let user choose Basic Pitch vs. Crepe)
5. **Build MIDI editor** (drag notes, delete, adjust velocity)

---

## Algorithm Comparison (For Later)

Once basic version works, you can add alternative algorithms:

| Algorithm | Speed | Monophonic Accuracy | Polyphonic Accuracy | Notes |
|-----------|-------|---------------------|---------------------|-------|
| **Basic Pitch** | Medium | 90% | 75% | Best all-around, Spotify's choice |
| **Crepe** | Slow | 95% | N/A | Monophonic only, very accurate |
| **pYIN** | Fast | 85% | N/A | Monophonic, good for vocals |
| **Omnizart** | Slow | 88% | 70% | Multiple instrument models |

**Recommendation**: Start with **Basic Pitch only**, add others later if needed.

---

## Testing Strategy

### Test Files You'll Need:
1. **Simple monophonic** - Single vocal line, bassline
2. **Simple polyphonic** - Piano chords, guitar strumming
3. **Complex polyphonic** - Piano solo, orchestral
4. **Edge cases** - Very quiet, very loud, distorted

### Success Criteria:
- ✅ Monophonic: 85%+ notes correct
- ⚠️ Polyphonic: 70%+ notes correct
- ⚠️ Timing: Within 50ms of actual onset
- ✅ No crashes on valid audio files

---

## Time Estimate

**Realistic Timeline** (solo developer, part-time):

- **Week 1**: CLI working, test with real stems
- **Week 2**: Add visualizations (waveform + piano roll)
- **Week 3**: Build PyQt6 GUI
- **Week 4**: Add MIDI editing tools
- **Week 5-6**: Polish, bug fixes, documentation

**Total**: 6 weeks to production-ready MVP

If full-time: 2-3 weeks

---

## Decision Time

### What to do right now:

1. ✅ **Validate the concept** (1 hour)
   - Install basic-pitch
   - Test on 3-5 real stems
   - Verify quality is acceptable

2. ✅ **Build CLI MVP** (2-4 hours)
   - Get stem → MIDI pipeline working
   - Test with different instruments

3. ✅ **Decide on GUI approach** (after CLI works)
   - Python desktop (PyQt6) - recommended
   - Web app (React + Python backend)
   - Electron app (if you want web tech + desktop distribution)

4. ✅ **Start building** (incremental improvements)

---

## Questions to Answer

Before diving in:

1. **Primary use case**: What stems will you process most? (piano, guitar, bass, vocals?)
2. **Platform**: macOS, Windows, Linux, or all three?
3. **Distribution**: Personal tool or share with others?
4. **Performance target**: Is 10-30 sec per stem acceptable?
5. **Editing needs**: How much manual correction do you expect?

Answer these, and I can tailor the implementation to your specific needs.

---

## My Recommendation

**Start here** (2-hour test):

```bash
# 1. Install dependencies
pip install basic-pitch librosa

# 2. Export a stem from your DAW
#    (bass, piano, or vocal - something tonal)

# 3. Run Basic Pitch CLI
basic-pitch output/ your_stem.wav

# 4. Load the MIDI in your DAW
#    How does it sound? How many errors?

# 5. If quality is acceptable → proceed with app
#    If quality is poor → may need different algorithm
```

This 2-hour test will tell you if the core technology meets your needs before investing in building the full app.

**Ready to start?** Let me know which path you want to take, and I'll set up the project skeleton!

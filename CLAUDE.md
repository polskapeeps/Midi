# CLAUDE.md — AI Assistant Guide for Audio to MIDI Extraction

This file provides context for AI assistants (Claude and others) working on this codebase. Read it before making any changes.

---

## Project Summary

**What it does**: Converts pre-separated audio stems (bass, piano, vocals, guitar, etc.) into MIDI files.

**Key design constraint**: Processes individual stems only — not full audio mixes. This trades source-separation capability for dramatically better speed and accuracy.

**Language**: Python 3.11+

**Current phase**: Phase 1 CLI MVP is code-complete; Phase 2 (user validation with real stems) is next.

---

## Repository Layout

```
Midi/
├── src/                     # Core application code
│   ├── __init__.py          # Package init (version 0.1.0)
│   ├── app.py               # CLI entry point — start here
│   ├── audio_loader.py      # File I/O, validation, format support
│   ├── pitch_detector.py    # Pitch detection (pYIN + Basic Pitch)
│   └── midi_exporter.py     # MIDI file generation
├── ui/
│   └── __init__.py          # Placeholder — GUI not yet started
├── tests/
│   ├── test_pitch_detector.py
│   └── test_midi_exporter.py
├── examples/
│   └── README.md            # Instructions for adding test stems (not tracked)
├── docs/                    # Future documentation
├── requirements.txt
├── .gitignore
├── README.md
├── DESIGN.md                # Full technical design (~730 lines) — read for deep context
├── GETTING_STARTED.md       # Developer onboarding
└── AGENT_GUIDE.md           # Legacy agent guide (superseded by this file)
```

---

## Processing Pipeline

```
Audio file (WAV/MP3/FLAC/OGG/M4A)
        ↓
  AudioLoader          — load, mono-convert, resample to 22050 Hz, validate duration
        ↓
  PitchDetector        — run pYIN or Basic Pitch, extract note events
        ↓
  (optional) filter    — remove low-confidence or too-short notes
  (optional) quantize  — snap note timings to rhythmic grid
        ↓
  MidiExporter         — write standard MIDI 1.0 .mid file
```

---

## Module Reference

### `src/app.py` — CLI Orchestrator

The main entry point. Instantiates the other three modules and runs them in sequence.

**CLI flags**:

| Flag | Default | Description |
|------|---------|-------------|
| `input` (positional) | — | Path to audio stem |
| `-o / --output` | auto-named | Output `.mid` path |
| `-a / --algorithm` | `pyin` | `pyin` or `basic-pitch` |
| `-t / --tempo` | `120` | BPM (20–400) |
| `-c / --confidence` | `0.3` | Min confidence threshold (0–1) |
| `-d / --min-duration` | `0.05` | Min note duration in seconds |
| `-q / --quantize` | off | Snap notes to rhythmic grid |
| `--quiet` | off | Suppress progress output |

### `src/audio_loader.py` — `AudioLoader`

- Supported formats: `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`
- Resamples to 22050 Hz, converts to mono
- Duration constraints: 0.5 s – 600 s (10 min)
- Raises `FileNotFoundError` for missing files, `ValueError` for invalid audio

### `src/pitch_detector.py` — `PitchDetector`

Two algorithms available:

| Algorithm | Accuracy | Speed | Python | Notes |
|-----------|----------|-------|--------|-------|
| `pyin` | Good for monophonic | Fast | 3.11+ / 3.12+ | Default; uses librosa |
| `basic-pitch` | Best overall | Slower | 3.11 only (TensorFlow) | Optional install |

pYIN config: frame_length=2048, hop_length=512, pitch range C2–C7.

Note dictionary schema returned by `detect()`:
```python
{
    'start_time': float,     # seconds
    'end_time':   float,     # seconds
    'duration':   float,     # seconds
    'pitch':      int,       # MIDI note number 0–127
    'velocity':   float,     # 0.0–1.0
    'note_name':  str,       # e.g. "C4", "G#5"
    'confidence': float,     # algorithm confidence score
    'pitch_bends': list,     # optional bend data
}
```

### `src/midi_exporter.py` — `MidiExporter`

- Produces MIDI 1.0 format
- Default tempo: 120 BPM; ticks per beat: 480
- Default program: 0 (Acoustic Grand Piano)
- Key methods: `export()`, `set_tempo()`, `set_program()`, `_seconds_to_ticks()`

---

## Code Conventions

**Naming**:
- Classes: `PascalCase` (`AudioLoader`, `PitchDetector`, `MidiExporter`)
- Methods/functions: `snake_case`; private helpers prefixed with `_`
- Constants: `UPPER_CASE` (`DEFAULT_SR`, `MAX_DURATION`, `SUPPORTED_FORMATS`)

**Style**:
- Type hints on all public function signatures
- Google-style docstrings (`Args:`, `Returns:`, `Raises:`) on all public methods
- `ValueError` for bad parameter values; `FileNotFoundError` for missing files; `ImportError` for optional missing deps

**Example signature**:
```python
def process_audio(
    input_path: str,
    min_confidence: float = 0.3
) -> list[dict]:
    """
    Process audio file and extract notes.

    Args:
        input_path: Path to audio file.
        min_confidence: Minimum note confidence (0–1).

    Returns:
        List of note dictionaries with pitch, time, velocity.

    Raises:
        FileNotFoundError: If input file does not exist.
    """
```

---

## Development Setup

```bash
# Python 3.11 recommended (required for Basic Pitch)
python3.11 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Core dependencies (pYIN pipeline works here)
pip install -r requirements.txt

# Optional: Basic Pitch (higher accuracy, requires Python 3.11 + TensorFlow)
pip install basic-pitch

# Verify
python src/app.py --help
```

---

## Running the CLI

```bash
# Minimal — pYIN algorithm, auto-named output
python src/app.py stem.wav

# Full options
python src/app.py stem.wav -o output.mid -a basic-pitch -t 140 -q -c 0.5

# Quiet mode (no progress output)
python src/app.py stem.wav --quiet
```

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run individual test files
python -m unittest tests/test_pitch_detector.py
python -m unittest tests/test_midi_exporter.py
```

**Quality thresholds to maintain**:
- Monophonic stems: ≥ 85% note accuracy
- Simple polyphonic: ≥ 70% note accuracy
- Timing accuracy: ±50 ms of actual onset
- Processing speed: < 30 s for a 3-minute stem on a mid-range CPU

Tests use `tempfile.TemporaryDirectory()` for isolation. No test audio files are committed; add your own to `examples/`.

---

## Known Limitations

- **Drums**: Not pitch-based — not supported and out of scope
- **Full mixes**: App is for stems only; full-mix input gives poor results
- **Octave errors**: Bass lines may be detected an octave off
- **Vibrato/pitch bends**: May produce multiple short notes instead of a bend
- **Complex polyphonic content** (piano solos, orchestral): Expect 60–70% accuracy
- **Basic Pitch + Python 3.12**: Not compatible — use pYIN on Python 3.12+
- **Memory**: Basic Pitch requires ~2–4 GB RAM during inference

---

## Roadmap Status

| Phase | Status | Description |
|-------|--------|-------------|
| 1 — CLI MVP | ✅ Complete | Load → Detect → Filter → Quantize → Export |
| 2 — Validation | ⏳ Next | Test with real stems, tune params, add tests |
| 3 — GUI | ❌ Not started | PyQt6 desktop app with piano roll view |
| 4 — Advanced | ❌ Not started | Batch processing, MusicXML export, GPU accel |

**GUI planned features** (Phase 3): waveform display, drag-and-drop, piano roll, audio playback, MIDI note editing, settings panel.

---

## Decision Guidelines for AI Assistants

**When adding features**: Check the phase table above. Implement only Phase 2 items unless the user explicitly requests otherwise. Document future ideas in `DESIGN.md` or `AGENT_GUIDE.md` rather than implementing them.

**When MIDI quality is reported as poor**:
1. Is the input a full mix (not a stem)? → Explain the stem-only constraint
2. Is it monophonic? → Should be ≥85%; check confidence threshold
3. Is it polyphonic? → 70–80% is expected; suggest `-q` and tuning `-c`

**When adding audio format support**:
- Check librosa/soundfile compatibility first
- Update `AudioLoader.SUPPORTED_FORMATS`
- Add the extension to `.gitignore`
- Test with a real sample file

**Import paths** — the project is not installed as a package, so import style depends on working directory:
```python
# Running from repo root (recommended)
from src.audio_loader import AudioLoader

# Running from inside src/
from audio_loader import AudioLoader
```

**Do not**:
- Add a GUI before Phase 3 is explicitly started
- Commit audio files (`*.wav`, `*.mp3`, `*.flac`, `*.mid` are gitignored)
- Introduce GPU requirements without user approval (CPU-only is the MVP target)
- Skip type hints or docstrings on public methods

---

## Git Workflow

Active development branch: `claude/add-claude-documentation-cRHvP`

```bash
git pull origin claude/add-claude-documentation-cRHvP
# ... make changes ...
git add <specific files>
git commit -m "Short imperative description"
git push -u origin claude/add-claude-documentation-cRHvP
```

Always push to the designated `claude/` branch. Never force-push or amend published commits.

---

## Key Reference Documents

| File | Purpose |
|------|---------|
| `DESIGN.md` | Full technical design, algorithm comparison, risk analysis |
| `GETTING_STARTED.md` | Step-by-step developer onboarding |
| `AGENT_GUIDE.md` | Legacy agent guide with decision trees and communication templates |
| `requirements.txt` | Python dependency versions |

# Agent Guide - Audio to MIDI Extraction Project

**Purpose**: This document provides AI agents/assistants with context about the project's architecture, current state, and implementation roadmap to streamline collaboration and maintain consistency.

---

## Project Overview

### What We're Building
An **audio-to-MIDI extraction application** that converts pre-separated audio stems (bass, piano, vocals, guitar, etc.) into MIDI files.

### Key Design Decision
**Simplified Scope**: Process individual stems (not full mixes) to:
- Reduce computational requirements by 80%+
- Achieve higher accuracy (85-95% monophonic, 70-80% polyphonic)
- Skip the slowest processing step (AI source separation)
- Let users leverage their DAW's existing stem separation tools

### Core Value Proposition
```
Separated Stem (WAV/MP3) → Pitch Detection → MIDI Export
     ↓
  [Our App]
     ↓
  Clean MIDI file (10-30 seconds processing)
```

---

## Current State

### ✅ Completed (as of initial setup)

1. **Design Phase**
   - Comprehensive technical design in `DESIGN.md` (60+ pages)
   - Architecture defined
   - Technology stack chosen: Python 3.11+, Basic Pitch, librosa, mido
   - Realistic performance expectations documented

2. **Project Structure**
   - Complete Python package structure (`src/`, `ui/`, `tests/`, `examples/`)
   - Core modules implemented (audio_loader, pitch_detector, midi_exporter)
   - CLI application (`app.py`) ready for testing
   - Dependencies defined in `requirements.txt`

3. **Documentation**
   - `README.md` - Project overview
   - `DESIGN.md` - Full technical design and analysis
   - `GETTING_STARTED.md` - Developer onboarding guide
   - `AGENT_GUIDE.md` - This file

4. **Git Setup**
   - Branch: `claude/audio-midi-extraction-design-ONa2R`
   - All files committed and pushed
   - `.gitignore` configured

### ⏳ Next Steps (Pending User Decision)

User needs to choose path:
1. **Test concept first** (validate Basic Pitch quality with their audio)
2. **Install and run CLI** (start using the tool)
3. **Build GUI** (PyQt6 desktop app)

---

## Architecture Summary

### Processing Pipeline

```python
1. Audio Input (WAV/MP3/FLAC)
   ↓
2. AudioLoader
   - Load and validate audio
   - Convert to mono, resample to 22050 Hz
   - Check duration (0.5s - 10min)
   ↓
3. PitchDetector
   - Run Basic Pitch ML model
   - Extract note events (pitch, time, velocity)
   - Filter low-confidence notes
   - Optional: quantize to rhythmic grid
   ↓
4. MidiExporter
   - Convert notes to MIDI messages
   - Set tempo, program (instrument)
   - Save as .mid file
```

### Module Responsibilities

| Module | File | Purpose | Status |
|--------|------|---------|--------|
| Audio Loading | `src/audio_loader.py` | File I/O, validation, format support | ✅ Complete |
| Pitch Detection | `src/pitch_detector.py` | ML-based pitch tracking, note filtering | ✅ Complete (Basic Pitch only) |
| MIDI Export | `src/midi_exporter.py` | MIDI file generation | ✅ Complete |
| CLI App | `src/app.py` | Command-line interface | ✅ Complete |
| GUI | `ui/main_window.py` | Desktop application (PyQt6) | ❌ Not started |
| Tests | `tests/` | Unit tests | ❌ Not started |

---

## Key Technical Decisions

### 1. Algorithm Choice: Basic Pitch (Spotify)
**Why**:
- Best all-around performance (90% monophonic, 75% polyphonic)
- Open-source (Apache 2.0 license)
- Instrument-agnostic
- Active maintenance

**Alternatives** (for future):
- CREPE (monophonic only, very accurate)
- pYIN (fast, good for vocals)
- Omnizart (multi-instrument models)

### 2. Language: Python
**Why**:
- Rich audio/ML ecosystem (librosa, Basic Pitch, mido)
- Fast prototyping
- Easy to iterate

**Trade-offs**:
- Slower than C++/Rust (acceptable for offline processing)
- Larger distribution size

### 3. GUI Framework: PyQt6 (when needed)
**Why**:
- Native desktop feel
- Cross-platform (macOS, Windows, Linux)
- Good performance for audio visualization

**Alternatives considered**:
- Web app (React + FastAPI backend)
- Electron (web tech + desktop distribution)

### 4. Simplified Scope: Stems Only
**Critical decision**: Don't include AI source separation in MVP
- Saves 80% processing time
- Reduces complexity
- Users can use DAW's built-in separation (Logic Pro, Ableton Live 12, FL Studio)

---

## Implementation Roadmap

### Phase 1: CLI MVP ✅ (Current)
**Duration**: 1-2 days
**Status**: Code complete, awaiting testing

**Features**:
- [x] Load audio files (WAV, MP3, FLAC)
- [x] Pitch detection (Basic Pitch)
- [x] Note filtering (confidence, duration)
- [x] MIDI export
- [x] CLI with arguments (tempo, quantization, etc.)

**Deliverable**: Working command-line tool

---

### Phase 2: Validation & Refinement ⏳ (Next)
**Duration**: 1-2 weeks
**Status**: Not started (waiting for user to test)

**Tasks**:
- [ ] User tests CLI with real stems
- [ ] Measure actual accuracy on different instrument types
- [ ] Identify common failure modes
- [ ] Tune filtering parameters
- [ ] Add unit tests

**Success Criteria**:
- 85%+ accuracy on monophonic content
- 70%+ accuracy on simple polyphonic content
- Processes 3-min stem in <30 seconds
- No crashes on valid audio

---

### Phase 3: GUI Application ⏳ (Future)
**Duration**: 2-3 weeks
**Status**: Not started

**Features to implement**:
- [ ] PyQt6 main window
- [ ] File browser / drag-and-drop
- [ ] Waveform visualization (matplotlib or pyqtgraph)
- [ ] Piano roll display with detected notes
- [ ] Audio playback controls
- [ ] MIDI editing tools (add/delete/move notes)
- [ ] Settings panel (algorithm, tempo, filtering)
- [ ] Export dialog with options

**Deliverable**: User-friendly desktop application

---

### Phase 4: Advanced Features ⏳ (Future)
**Duration**: 3-4 weeks
**Status**: Not started

**Potential features**:
- [ ] Multiple algorithm support (Basic Pitch + CREPE + pYIN)
- [ ] Batch processing
- [ ] Spectrogram visualization
- [ ] Pitch bend detection
- [ ] GPU acceleration
- [ ] Export to MusicXML (sheet music)
- [ ] VST/AU plugin version (DAW integration)
- [ ] Presets for different instruments

---

## Working with This Project

### When Starting a New Task

1. **Check current state**:
   ```bash
   git status
   git log --oneline -5
   ```

2. **Review relevant docs**:
   - This file (AGENT_GUIDE.md) - overall context
   - DESIGN.md - technical decisions and limitations
   - GETTING_STARTED.md - how to set up and test

3. **Understand the phase**:
   - Where are we in the roadmap?
   - What's been tested/validated?
   - What dependencies exist?

### Code Style Guidelines

**Python**:
- Type hints for function signatures
- Docstrings for all public methods (Google style)
- Classes for logical grouping
- Keep functions focused and testable
- Use descriptive variable names

**Example**:
```python
def process_audio(
    input_path: str,
    min_confidence: float = 0.3
) -> List[dict]:
    """
    Process audio file and extract notes.

    Args:
        input_path: Path to audio file
        min_confidence: Minimum note confidence (0-1)

    Returns:
        List of note dictionaries with pitch, time, velocity

    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    # Implementation...
```

### Testing Strategy

**For each module**:
1. Unit tests in `tests/test_<module>.py`
2. Test with real audio files (in `examples/`)
3. Validate edge cases (very short, very long, silent, corrupted)

**Quality thresholds**:
- Monophonic: 85%+ note accuracy
- Polyphonic: 70%+ note accuracy
- Timing: ±50ms of actual onset
- Processing: <30s for 3-min stem on mid-range laptop

### Common Issues & Solutions

#### Issue: Basic Pitch not installed
```bash
pip install basic-pitch
# May require tensorflow (installed automatically)
```

#### Issue: Import errors in src/
```python
# When running from src/ directory, use:
from audio_loader import AudioLoader

# When running as package, use:
from src.audio_loader import AudioLoader
```

#### Issue: Processing too slow
**Solutions**:
1. Check if running on CPU (expected: 10-30s per 3-min stem)
2. Consider GPU acceleration (requires CUDA setup)
3. For MVP: accept slower speed, optimize later

#### Issue: Poor MIDI quality
**Debugging steps**:
1. Check input audio quality (lossy formats reduce accuracy)
2. Verify stem is truly isolated (no bleed from other instruments)
3. Try different confidence thresholds (`-c 0.5` for stricter)
4. Use quantization (`-q` flag) for rhythmic material
5. Check if polyphonic (lower expected accuracy)

---

## Technical Constraints & Limitations

### What Works Well ✅
- **Monophonic content** (vocals, bass, single melody): 85-95% accuracy
- **Simple polyphonic** (guitar chords, simple piano): 70-80% accuracy
- **Clean audio** (properly separated stems): High quality
- **Pop/rock/electronic music**: Best results (models trained on this)

### Known Limitations ⚠️
- **Complex polyphonic** (piano solos, orchestral): 60-70% accuracy
- **Octave errors**: Bass can be detected wrong octave
- **Harmonic confusion**: Strong harmonics mistaken for notes
- **Vibrato/pitch bends**: Creates multiple notes instead of bend
- **Fast passages**: May miss or merge notes
- **Drums**: Not pitch-based, requires different approach (not implemented)

### Performance Targets
- **Processing time**: 10-30 seconds per 3-min stem (CPU)
- **Memory usage**: ~2-4GB during processing
- **File size limits**: 0.5s minimum, 10 minutes maximum
- **Supported formats**: WAV, MP3, FLAC, OGG, M4A

---

## Decision Trees for Agents

### When User Reports "MIDI Quality is Poor"

```
Is the input a separated stem or full mix?
├─ Full mix → Explain: App designed for stems only
│             Suggest: Use DAW's stem separation first
│
└─ Separated stem →
   │
   Is it monophonic or polyphonic?
   ├─ Monophonic → Should be 85%+ accurate
   │              Check: Confidence threshold too high?
   │              Try: Lower -c value (default 0.3)
   │
   └─ Polyphonic → Expected 70-80% accuracy
                   Explain: Manual editing needed
                   Suggest: Use quantization (-q flag)
                           Try different confidence values
```

### When Adding a New Feature

```
Does it fit the current phase?
├─ Yes → Implement with tests
│
└─ No → Document in roadmap for later phase
        Ask user if priority should shift
```

### When User Asks "Can we support [new format]?"

```
Is it audio format?
├─ Yes → Check librosa/soundfile compatibility
│        Update AudioLoader.SUPPORTED_FORMATS
│        Add to .gitignore if needed
│        Test with sample file
│
└─ No (e.g., video) → Out of scope for MVP
                      Document as future enhancement
```

---

## File Organization

```
Midi/
├── DESIGN.md              # Full technical design (READ FIRST for deep context)
├── GETTING_STARTED.md     # User/developer onboarding guide
├── AGENT_GUIDE.md         # This file - agent workflow guide
├── README.md              # Project overview
├── requirements.txt       # Python dependencies
├── .gitignore            # Git exclusions
│
├── src/                   # Core application code
│   ├── __init__.py       # Package initialization
│   ├── app.py            # CLI entry point ⭐ START HERE
│   ├── audio_loader.py   # Audio I/O and validation
│   ├── pitch_detector.py # ML pitch detection (Basic Pitch)
│   └── midi_exporter.py  # MIDI file creation
│
├── ui/                    # GUI code (not started)
│   └── __init__.py
│
├── tests/                 # Unit tests (not started)
│   └── __init__.py
│
├── examples/              # Test audio files (user adds these)
│   └── README.md
│
└── docs/                  # Additional documentation (future)
```

---

## Quick Reference Commands

### Setup & Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test installation
cd src && python app.py --help
```

### Running the CLI
```bash
# Basic usage
python src/app.py path/to/stem.wav

# With options
python src/app.py input.wav -o output.mid -t 140 -q -c 0.5

# Help
python src/app.py --help
```

### Git Workflow
```bash
# Always work on feature branch: claude/audio-midi-extraction-design-ONa2R
git status
git add <files>
git commit -m "Clear description of changes"
git push -u origin claude/audio-midi-extraction-design-ONa2R
```

### Testing Workflow
```bash
# Manual test with example file
python src/app.py examples/bass_stem.wav -o test_output.mid -v

# Check output
ls -lh test_output.mid

# Load in DAW and verify quality
```

---

## Communication Guidelines

### When Updating User on Progress

**Good**:
```
✅ Implemented waveform visualization using matplotlib
⚠️ Note: Rendering may be slow for files >5 minutes
📊 Tested with 3 sample files - all working correctly
```

**Avoid**:
```
Done. [Too brief, no context]
I made some changes to the code. [Vague]
```

### When Encountering Issues

**Report**:
1. What you were trying to do
2. What went wrong (error message, unexpected behavior)
3. What you tried to fix it
4. Recommendations for next steps

**Example**:
```
⚠️ Issue: Basic Pitch failing on MP3 files

Attempted:
- Verified librosa can load MP3s ✅
- Checked Basic Pitch version (0.3.0) ✅
- Tested with WAV file (works fine) ✅

Root cause: MP3 needs audioread backend
Solution: Add audioread to requirements.txt
```

### When Proposing Changes

**Include**:
1. Why the change is needed
2. What will be different
3. Any trade-offs or risks
4. How to test/validate

---

## Success Metrics

### MVP Success (Phase 1-2)
- [ ] User successfully converts 5+ stems to MIDI
- [ ] 80%+ of notes are correct (user reports)
- [ ] Processing time <30s per 3-min stem
- [ ] Zero crashes on valid audio files
- [ ] User finds tool valuable (saves time vs. manual MIDI entry)

### Long-term Success (Phase 3-4)
- [ ] GUI application used regularly by user
- [ ] Supports 3+ pitch detection algorithms
- [ ] Batch processing capability
- [ ] Community adoption (if open-sourced)

---

## Resources & References

### Documentation
- **Basic Pitch**: https://github.com/spotify/basic-pitch
- **librosa**: https://librosa.org/doc/latest/index.html
- **mido**: https://mido.readthedocs.io/en/latest/
- **PyQt6**: https://doc.qt.io/qtforpython/

### Academic Papers
- Basic Pitch paper: "A Lightweight Instrument-Agnostic Model for Polyphonic Note Transcription" (ICASSP 2022)
- See DESIGN.md for full bibliography

### Similar Projects
- Spotify's Basic Pitch (CLI only)
- AnthemScore (commercial, $29-99)
- Melodyne (commercial, $99-849, industry standard)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-02 | Initial project setup, CLI MVP complete | Claude |

---

## Notes for Future Agents

### Context Preservation
- Always read this file when starting work on the project
- Update roadmap status when completing tasks
- Document new decisions in appropriate sections
- Keep "Current State" section up to date

### Avoiding Scope Creep
- Stick to current phase goals
- Document future ideas in roadmap
- Ask user before shifting priorities
- Remember: MVP is about validation, not perfection

### Quality Over Speed
- Test with real audio before marking complete
- Write tests for new functionality
- Document limitations honestly
- Prioritize user needs over feature count

---

## Contact & Collaboration

When multiple agents/sessions work on this project:
1. Always pull latest changes before starting: `git pull origin claude/audio-midi-extraction-design-ONa2R`
2. Update this guide when making architectural decisions
3. Keep roadmap status current
4. Document any deviations from plan with reasoning

---

**Last Updated**: 2026-01-02
**Project Phase**: Phase 1 (CLI MVP) - Awaiting user validation
**Next Action**: User to test CLI with real stems or install dependencies

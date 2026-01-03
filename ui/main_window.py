"""PyQt6 GUI for the Audio-to-MIDI pipeline.

This module provides a thin GUI wrapper around the existing
`AudioToMidiApp` CLI workflow. It is intentionally minimal so we can
iterate on layout and optional features while keeping the backend logic
unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PyQt6 import QtCore, QtWidgets

# Ensure repository root is on sys.path so we can import backend modules
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
for path in (PROJECT_ROOT, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from src.app import AudioToMidiApp  # noqa: E402  pylint: disable=wrong-import-position


class ConversionWorker(QtCore.QThread):
    """Run the audio-to-MIDI conversion off the UI thread."""

    progress = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(str)
    failed = QtCore.pyqtSignal(str)

    def __init__(
        self,
        input_path: str,
        output_path: Optional[str],
        algorithm: str,
        tempo: int,
        min_confidence: float,
        min_duration: float,
        quantize: bool,
        parent: Optional[QtCore.QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.input_path = input_path
        self.output_path = output_path
        self.algorithm = algorithm
        self.tempo = tempo
        self.min_confidence = min_confidence
        self.min_duration = min_duration
        self.quantize = quantize

    def run(self) -> None:  # pragma: no cover - UI thread entrypoint
        try:
            app = AudioToMidiApp(
                algorithm=self.algorithm,
                tempo=self.tempo,
                min_confidence=self.min_confidence,
                min_duration=self.min_duration,
            )
            self.progress.emit("Starting conversion...")
            output = app.process(
                input_path=self.input_path,
                output_path=self.output_path,
                quantize=self.quantize,
                verbose=False,
            )
            if output:
                self.finished.emit(output)
            else:
                self.failed.emit("No notes detected; nothing to export.")
        except Exception as exc:  # pragma: no cover - defensive guard
            self.failed.emit(str(exc))


class MainWindow(QtWidgets.QMainWindow):
    """Primary GUI window for configuring conversions."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Audio to MIDI Converter (Preview)")
        self.resize(900, 520)

        self._central = QtWidgets.QWidget()
        self.setCentralWidget(self._central)

        self._build_layout()
        self._wire_signals()

        self.worker: Optional[ConversionWorker] = None

    def _build_layout(self) -> None:
        main_layout = QtWidgets.QVBoxLayout()

        # File selectors
        file_group = QtWidgets.QGroupBox("File Paths")
        file_layout = QtWidgets.QGridLayout()
        file_group.setLayout(file_layout)

        self.input_edit = QtWidgets.QLineEdit()
        self.output_edit = QtWidgets.QLineEdit()
        self.browse_input_btn = QtWidgets.QPushButton("Browse Input…")
        self.browse_output_btn = QtWidgets.QPushButton("Browse Output…")

        file_layout.addWidget(QtWidgets.QLabel("Input audio"), 0, 0)
        file_layout.addWidget(self.input_edit, 0, 1)
        file_layout.addWidget(self.browse_input_btn, 0, 2)

        file_layout.addWidget(QtWidgets.QLabel("Output MIDI"), 1, 0)
        file_layout.addWidget(self.output_edit, 1, 1)
        file_layout.addWidget(self.browse_output_btn, 1, 2)

        # Settings
        settings_group = QtWidgets.QGroupBox("Processing Settings")
        settings_layout = QtWidgets.QGridLayout()
        settings_group.setLayout(settings_layout)

        self.algorithm_combo = QtWidgets.QComboBox()
        self.algorithm_combo.addItems(["pyin", "basic-pitch", "drums"])
        self.algorithm_combo.setCurrentText("pyin")

        self.tempo_spin = QtWidgets.QSpinBox()
        self.tempo_spin.setRange(40, 240)
        self.tempo_spin.setValue(120)

        self.confidence_spin = QtWidgets.QDoubleSpinBox()
        self.confidence_spin.setRange(0.0, 1.0)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setValue(0.30)

        self.duration_spin = QtWidgets.QDoubleSpinBox()
        self.duration_spin.setRange(0.01, 2.0)
        self.duration_spin.setSingleStep(0.01)
        self.duration_spin.setValue(0.05)

        self.quantize_check = QtWidgets.QCheckBox("Quantize to grid (4ths)")

        settings_layout.addWidget(QtWidgets.QLabel("Algorithm"), 0, 0)
        settings_layout.addWidget(self.algorithm_combo, 0, 1)
        settings_layout.addWidget(QtWidgets.QLabel("Tempo (BPM)"), 1, 0)
        settings_layout.addWidget(self.tempo_spin, 1, 1)
        settings_layout.addWidget(QtWidgets.QLabel("Min confidence"), 2, 0)
        settings_layout.addWidget(self.confidence_spin, 2, 1)
        settings_layout.addWidget(QtWidgets.QLabel("Min duration (s)"), 3, 0)
        settings_layout.addWidget(self.duration_spin, 3, 1)
        settings_layout.addWidget(self.quantize_check, 4, 0, 1, 2)

        # Action buttons
        self.convert_btn = QtWidgets.QPushButton("Convert to MIDI")
        self.convert_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.convert_btn.setEnabled(True)

        # Log area
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Logs and status messages will appear here…")

        main_layout.addWidget(file_group)
        main_layout.addWidget(settings_group)
        main_layout.addWidget(self.convert_btn)
        main_layout.addWidget(self.log_output, stretch=1)

        self._central.setLayout(main_layout)

    def _wire_signals(self) -> None:
        self.browse_input_btn.clicked.connect(self._select_input)
        self.browse_output_btn.clicked.connect(self._select_output)
        self.convert_btn.clicked.connect(self._start_conversion)

    # ----- Slots -----
    def _select_input(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select input audio",
            str(PROJECT_ROOT),
            "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a)",
        )
        if file_path:
            self.input_edit.setText(file_path)
            suggested = Path(file_path).with_suffix(".mid")
            self.output_edit.setText(str(suggested))

    def _select_output(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select output MIDI",
            self.output_edit.text() or str(PROJECT_ROOT),
            "MIDI Files (*.mid)",
        )
        if file_path:
            if not file_path.lower().endswith(".mid"):
                file_path = f"{file_path}.mid"
            self.output_edit.setText(file_path)

    def _start_conversion(self) -> None:
        input_path = self.input_edit.text().strip()
        if not input_path:
            self._append_log("Please select an input audio file.")
            return

        if not Path(input_path).exists():
            self._append_log("Selected input file does not exist.")
            return

        output_path = self.output_edit.text().strip() or None

        self.convert_btn.setEnabled(False)
        self._append_log("Starting conversion… this may take a moment.")

        self.worker = ConversionWorker(
            input_path=input_path,
            output_path=output_path,
            algorithm=self.algorithm_combo.currentText(),
            tempo=self.tempo_spin.value(),
            min_confidence=self.confidence_spin.value(),
            min_duration=self.duration_spin.value(),
            quantize=self.quantize_check.isChecked(),
        )

        self.worker.progress.connect(self._append_log)
        self.worker.finished.connect(self._handle_success)
        self.worker.failed.connect(self._handle_failure)
        self.worker.finished.connect(self._finalize_worker)
        self.worker.failed.connect(self._finalize_worker)
        self.worker.start()

    def _handle_success(self, output_path: str) -> None:
        self._append_log(f"✅ Conversion complete. Saved to: {output_path}")
        QtWidgets.QMessageBox.information(self, "Conversion complete", f"MIDI saved to:\n{output_path}")

    def _handle_failure(self, message: str) -> None:
        self._append_log(f"❌ Conversion failed: {message}")
        QtWidgets.QMessageBox.critical(self, "Conversion failed", message)

    def _finalize_worker(self) -> None:
        self.convert_btn.setEnabled(True)
        self.worker = None

    def _append_log(self, message: str) -> None:
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""Settings window GUI."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QLineEdit,
    QMessageBox, QTabWidget, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence, QKeyEvent
from typing import Optional


class SettingsWindow(QWidget):
    """Settings window for configuring the application."""
    
    closed = pyqtSignal()
    
    def __init__(self, config, audio_capture, stt_engine):
        """Initialize settings window.
        
        Args:
            config: Configuration object
            audio_capture: AudioCapture instance
            stt_engine: STTEngine instance
        """
        super().__init__()
        self.config = config
        self.audio_capture = audio_capture
        self.stt_engine = stt_engine
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("VocalNode Settings")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Hotkey tab
        hotkey_tab = self.create_hotkey_tab()
        tabs.addTab(hotkey_tab, "Hotkey")
        
        # Audio tab
        audio_tab = self.create_audio_tab()
        tabs.addTab(audio_tab, "Audio")
        
        # Speech-to-Text tab
        stt_tab = self.create_stt_tab()
        tabs.addTab(stt_tab, "Speech-to-Text")
        
        # Overlay tab
        overlay_tab = self.create_overlay_tab()
        tabs.addTab(overlay_tab, "Overlay")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_hotkey_tab(self) -> QWidget:
        """Create hotkey configuration tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Key capture button
        self.key_capture_button = QPushButton("Click here and press your hotkey")
        self.key_capture_button.setMinimumHeight(40)
        self.key_capture_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.key_capture_button.clicked.connect(self.start_key_capture)
        self.capturing_key = False
        self.captured_key = None
        self.captured_modifiers = []
        
        # Current hotkey display
        self.current_hotkey_label = QLabel("Current: Not set")
        self.current_hotkey_label.setStyleSheet("font-weight: bold; color: #333;")
        
        key_layout = QVBoxLayout()
        key_layout.addWidget(self.key_capture_button)
        key_layout.addWidget(self.current_hotkey_label)
        layout.addRow("Hotkey:", key_layout)
        
        # Initialize from config (after label is created)
        self._initialize_hotkey_display()
        
        # Mode
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Toggle (press to start/stop)")
        self.mode_combo.addItem("Hold (hold to record)")
        layout.addRow("Mode:", self.mode_combo)
        
        # Instructions
        instructions = QLabel(
            "Click the button above, then press your desired hotkey combination.\n"
            "You can use any key with optional modifiers (Ctrl, Alt, Shift, Cmd/Meta)."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-size: 11px;")
        layout.addRow("", instructions)
        
        widget.setLayout(layout)
        return widget
    
    def _initialize_hotkey_display(self):
        """Initialize hotkey display from config."""
        key = self.config.get("hotkey.key", "f8")
        modifiers = self.config.get("hotkey.modifiers", [])
        self.captured_key = key
        self.captured_modifiers = [m.lower() for m in modifiers]
        mod_str = "+".join([m.capitalize() for m in self.captured_modifiers])
        display = f"{mod_str}+{key}" if mod_str else key
        self.current_hotkey_label.setText(f"Current: {display}")
    
    def start_key_capture(self):
        """Start capturing key press."""
        self.capturing_key = True
        self.key_capture_button.setText("Press your hotkey now...")
        self.key_capture_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        # Ensure window is active and focused
        self.raise_()
        self.activateWindow()
        self.setFocus()
        self.key_capture_button.setFocus()
        # Install event filter to capture keys
        # Install on the application to catch all key events
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().installEventFilter(self)
        print("[DEBUG] Key capture started - press any key now")
    
    def eventFilter(self, obj, event):
        """Filter events to capture key presses."""
        if self.capturing_key and event.type() == event.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            print(f"[DEBUG] Key captured: key={key}, modifiers={modifiers}")
            
            # Convert Qt key to string representation
            key_str = self._qt_key_to_string(key, modifiers)
            
            print(f"[DEBUG] Converted to string: {key_str}")
            
            if key_str:
                self.captured_key = key_str
                self.captured_modifiers = []
                
                # Extract modifiers
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    self.captured_modifiers.append("ctrl")
                if modifiers & Qt.KeyboardModifier.AltModifier:
                    self.captured_modifiers.append("alt")
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    self.captured_modifiers.append("shift")
                if modifiers & Qt.KeyboardModifier.MetaModifier:
                    self.captured_modifiers.append("cmd")
                
                # Update display
                mod_str = "+".join([m.capitalize() for m in self.captured_modifiers])
                display = f"{mod_str}+{key_str}" if mod_str else key_str
                self.current_hotkey_label.setText(f"Current: {display}")
                self.key_capture_button.setText("Click to change hotkey")
                self.key_capture_button.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 10px;
                        background-color: #f0f0f0;
                        border: 2px solid #ccc;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """)
                self.capturing_key = False
                # Remove event filter from application
                from PyQt6.QtWidgets import QApplication
                QApplication.instance().removeEventFilter(self)
                print(f"[DEBUG] Key capture complete: {display}")
                return True
        
        return super().eventFilter(obj, event)
    
    def _qt_key_to_string(self, key, modifiers):
        """Convert Qt key code to string representation."""
        # Handle special keys
        special_keys = {
            Qt.Key.Key_F1: "f1", Qt.Key.Key_F2: "f2", Qt.Key.Key_F3: "f3",
            Qt.Key.Key_F4: "f4", Qt.Key.Key_F5: "f5", Qt.Key.Key_F6: "f6",
            Qt.Key.Key_F7: "f7", Qt.Key.Key_F8: "f8", Qt.Key.Key_F9: "f9",
            Qt.Key.Key_F10: "f10", Qt.Key.Key_F11: "f11", Qt.Key.Key_F12: "f12",
            Qt.Key.Key_Space: "space",
            Qt.Key.Key_Insert: "insert", Qt.Key.Key_Delete: "delete",
            Qt.Key.Key_Home: "home", Qt.Key.Key_End: "end",
            Qt.Key.Key_PageUp: "page_up", Qt.Key.Key_PageDown: "page_down",
            Qt.Key.Key_Up: "up", Qt.Key.Key_Down: "down",
            Qt.Key.Key_Left: "left", Qt.Key.Key_Right: "right",
            Qt.Key.Key_Enter: "enter", Qt.Key.Key_Return: "return",
            Qt.Key.Key_Tab: "tab", Qt.Key.Key_Backspace: "backspace",
            Qt.Key.Key_Escape: "escape",
        }
        
        if key in special_keys:
            return special_keys[key]
        
        # Handle regular character keys
        if key >= Qt.Key.Key_A and key <= Qt.Key.Key_Z:
            char = chr(key)
            # Check if shift is pressed for uppercase
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                return char.upper()
            return char.lower()
        
        # Handle number keys
        if key >= Qt.Key.Key_0 and key <= Qt.Key.Key_9:
            # Map Qt key codes to characters
            num_map = {
                Qt.Key.Key_0: '0', Qt.Key.Key_1: '1', Qt.Key.Key_2: '2',
                Qt.Key.Key_3: '3', Qt.Key.Key_4: '4', Qt.Key.Key_5: '5',
                Qt.Key.Key_6: '6', Qt.Key.Key_7: '7', Qt.Key.Key_8: '8',
                Qt.Key.Key_9: '9'
            }
            return num_map.get(key, chr(key))
        
        # Try to get key sequence
        try:
            seq = QKeySequence(key)
            text = seq.toString()
            if text:
                return text.lower()
        except:
            pass
        
        return None
    
    def create_audio_tab(self) -> QWidget:
        """Create audio configuration tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Device selection
        self.device_combo = QComboBox()
        self.refresh_devices()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_devices)
        device_layout = QHBoxLayout()
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(refresh_btn)
        layout.addRow("Audio Device:", device_layout)
        
        # Sample rate
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["8000", "16000", "44100", "48000"])
        layout.addRow("Sample Rate:", self.sample_rate_combo)
        
        widget.setLayout(layout)
        return widget
    
    def create_stt_tab(self) -> QWidget:
        """Create speech-to-text configuration tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        layout.addRow("Model:", self.model_combo)
        
        # Language selection
        self.language_combo = QComboBox()
        # Common languages
        languages = [
            ("auto", "Auto-detect"),
            ("en", "English"),
            ("es", "Spanish"),
            ("fr", "French"),
            ("de", "German"),
            ("it", "Italian"),
            ("pt", "Portuguese"),
            ("ru", "Russian"),
            ("ja", "Japanese"),
            ("zh", "Chinese"),
            ("ko", "Korean"),
        ]
        for code, name in languages:
            self.language_combo.addItem(f"{name} ({code})", code)
        layout.addRow("Language:", self.language_combo)
        
        # Device (CPU/CUDA)
        self.device_combo_stt = QComboBox()
        self.device_combo_stt.addItems(["cpu", "cuda"])
        layout.addRow("Compute Device:", self.device_combo_stt)
        
        widget.setLayout(layout)
        return widget
    
    def create_overlay_tab(self) -> QWidget:
        """Create overlay configuration tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Enable overlay
        self.overlay_enabled_check = QCheckBox("Show dictation overlay")
        layout.addRow(self.overlay_enabled_check)
        
        # Position
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "Top Left",
            "Top Right",
            "Bottom Left",
            "Bottom Right",
            "Center"
        ])
        layout.addRow("Position:", self.position_combo)
        
        # Show text
        self.show_text_check = QCheckBox("Show transcribed text preview")
        layout.addRow(self.show_text_check)
        
        # Opacity
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(10, 100)
        self.opacity_spin.setSuffix("%")
        layout.addRow("Opacity:", self.opacity_spin)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_devices(self):
        """Refresh list of audio devices."""
        self.device_combo.clear()
        devices = self.audio_capture.list_devices()
        self.device_combo.addItem("Default Device", None)
        for device in devices:
            self.device_combo.addItem(
                f"{device['name']} ({device['channels']}ch, {int(device['sample_rate'])}Hz)",
                device['id']
            )
    
    def load_settings(self):
        """Load current settings into UI."""
        # Hotkey settings
        key = self.config.get("hotkey.key", "f8")
        modifiers = self.config.get("hotkey.modifiers", [])
        
        # Set captured key and modifiers
        self.captured_key = key
        self.captured_modifiers = [m.lower() for m in modifiers]
        
        # Update display
        mod_str = "+".join([m.capitalize() for m in self.captured_modifiers])
        display = f"{mod_str}+{key}" if mod_str else key
        self.current_hotkey_label.setText(f"Current: {display}")
        self.key_capture_button.setText("Click to change hotkey")
        
        mode = self.config.get("hotkey.mode", "toggle")
        self.mode_combo.setCurrentIndex(0 if mode == "toggle" else 1)
        
        # Audio settings
        device_id = self.config.get("audio.device_id")
        for i in range(self.device_combo.count()):
            if self.device_combo.itemData(i) == device_id:
                self.device_combo.setCurrentIndex(i)
                break
        
        sample_rate = str(int(self.config.get("audio.sample_rate", 16000)))
        index = self.sample_rate_combo.findText(sample_rate)
        if index >= 0:
            self.sample_rate_combo.setCurrentIndex(index)
        
        # STT settings
        model = self.config.get("stt.model", "base")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        
        language = self.config.get("stt.language", "en")
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == language:
                self.language_combo.setCurrentIndex(i)
                break
        
        device = self.config.get("stt.device", "cpu")
        self.device_combo_stt.setCurrentIndex(0 if device == "cpu" else 1)
        
        # Overlay settings
        self.overlay_enabled_check.setChecked(self.config.get("overlay.enabled", True))
        
        position = self.config.get("overlay.position", "bottom_right")
        position_map = {
            "top_left": 0,
            "top_right": 1,
            "bottom_left": 2,
            "bottom_right": 3,
            "center": 4
        }
        self.position_combo.setCurrentIndex(position_map.get(position, 3))
        
        self.show_text_check.setChecked(self.config.get("overlay.show_text", True))
        
        opacity = int(self.config.get("overlay.opacity", 0.9) * 100)
        self.opacity_spin.setValue(opacity)
    
    def save_settings(self):
        """Save settings from UI to config."""
        try:
            # Hotkey settings
            if self.captured_key:
                self.config.set("hotkey.key", self.captured_key.lower())
                self.config.set("hotkey.modifiers", self.captured_modifiers)
            else:
                # Fallback to default if nothing captured
                self.config.set("hotkey.key", "f8")
                self.config.set("hotkey.modifiers", [])
            
            mode = "toggle" if self.mode_combo.currentIndex() == 0 else "hold"
            self.config.set("hotkey.mode", mode)
            
            # Audio settings
            device_id = self.device_combo.currentData()
            self.config.set("audio.device_id", device_id)
            
            sample_rate = int(self.sample_rate_combo.currentText())
            self.config.set("audio.sample_rate", sample_rate)
            
            # STT settings
            model = self.model_combo.currentText()
            self.config.set("stt.model", model)
            self.stt_engine.set_model(model)
            
            language = self.language_combo.currentData()
            self.config.set("stt.language", language)
            self.stt_engine.set_language(language)
            
            device = self.device_combo_stt.currentText()
            self.config.set("stt.device", device)
            
            # Overlay settings
            self.config.set("overlay.enabled", self.overlay_enabled_check.isChecked())
            
            position_map = ["top_left", "top_right", "bottom_left", "bottom_right", "center"]
            position = position_map[self.position_combo.currentIndex()]
            self.config.set("overlay.position", position)
            
            self.config.set("overlay.show_text", self.show_text_check.isChecked())
            
            opacity = self.opacity_spin.value() / 100.0
            self.config.set("overlay.opacity", opacity)
            
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.closed.emit()
        super().closeEvent(event)


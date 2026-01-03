"""Main application entry point."""

import sys
import threading
import time
import json
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

# #region agent log
DEBUG_LOG_PATH = "/home/jb/dev/VocalNode/.cursor/debug.log"
def _debug_log(session_id, run_id, hypothesis_id, location, message, data=None):
    try:
        with open(DEBUG_LOG_PATH, 'a') as f:
            log_entry = {
                "sessionId": session_id,
                "runId": run_id,
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data or {},
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + "\n")
    except:
        pass
# #endregion

from .config import Config
from .tray_icon import TrayIcon
from .settings_window import SettingsWindow
from .hotkey_manager import HotkeyManager
from .audio_capture import AudioCapture
from .stt_engine import STTEngine
from .dictation_overlay import DictationOverlay
from .text_inserter import TextInserter


class VocalNodeApp(QObject):
    """Main application class."""
    
    # Signals for thread-safe communication
    text_ready = pyqtSignal(str)
    processing_done = pyqtSignal()
    show_message_signal = pyqtSignal(str, str, object)  # title, message, icon_type
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Initialize components
        self.config = Config()
        self.audio_capture = AudioCapture(self.config)
        self.stt_engine = STTEngine(self.config)
        self.text_inserter = TextInserter(self.config)
        
        # Initialize GUI components
        self.tray_icon = TrayIcon()
        self.overlay = DictationOverlay(self.config)
        self.settings_window = None
        
        # State
        self.is_recording = False
        self.is_processing = False
        self.audio_chunks = []
        self.recording_thread = None
        
        # Setup hotkey manager
        self.hotkey_manager = HotkeyManager(
            self.config,
            on_press=self.start_dictation,
            on_release=self.stop_dictation
        )
        
        # Connect signals
        self.tray_icon.show_settings.connect(self.show_settings)
        self.tray_icon.toggle_dictation.connect(self.toggle_dictation)
        self.tray_icon.quit_app.connect(self.quit_application)
        self.text_ready.connect(self._insert_text)
        # #region agent log
        _debug_log("debug-session", "run1", "H4", "main.py:__init__:signal_connect", "text_ready signal connected", {"handler": "_insert_text"})
        # #endregion
        self.processing_done.connect(self._on_processing_done)
        # #region agent log
        _debug_log("debug-session", "run1", "H4", "main.py:__init__:signal_connect", "processing_done signal connected", {"handler": "_on_processing_done"})
        # #endregion
        self.show_message_signal.connect(self._show_message)
        # #region agent log
        _debug_log("debug-session", "run1", "H4", "main.py:__init__:signal_connect", "show_message_signal connected", {"handler": "_show_message"})
        # #endregion
        
        # Start hotkey listener
        # #region agent log
        _debug_log("debug-session", "run1", "H1", "main.py:__init__:before_hotkey_start", "Before starting hotkey manager")
        # #endregion
        hotkey_start_result = self.hotkey_manager.start()
        # #region agent log
        _debug_log("debug-session", "run1", "H1", "main.py:__init__:after_hotkey_start", "After starting hotkey manager", {"result": hotkey_start_result, "listener_exists": self.hotkey_manager.listener is not None})
        # #endregion
        
        # Load STT model in background
        self.load_model_async()
    
    def load_model_async(self):
        """Load STT model in background thread."""
        def load():
            try:
                self.stt_engine.load_model()
                self.show_message_signal.emit(
                    "VocalNode",
                    "Model loaded successfully",
                    self.tray_icon.tray_icon.MessageIcon.Information
                )
            except Exception as e:
                self.show_message_signal.emit(
                    "VocalNode",
                    f"Error loading model: {e}",
                    self.tray_icon.tray_icon.MessageIcon.Critical
                )
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def _show_message(self, title: str, message: str, icon_type: int):
        """Show message (runs on main thread)."""
        self.tray_icon.show_message(title, message, icon_type)
    
    def show_settings(self):
        """Show settings window."""
        if self.settings_window is None:
            self.settings_window = SettingsWindow(
                self.config,
                self.audio_capture,
                self.stt_engine
            )
            self.settings_window.closed.connect(self.on_settings_closed)
        
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
    
    def on_settings_closed(self):
        """Handle settings window closed."""
        # Settings are saved automatically, but we may need to restart hotkey listener
        self.hotkey_manager.stop()
        self.hotkey_manager = HotkeyManager(
            self.config,
            on_press=self.start_dictation,
            on_release=self.stop_dictation
        )
        self.hotkey_manager.start()
        
        # Update overlay position if changed
        self.overlay.update_position()
    
    def toggle_dictation(self):
        """Toggle dictation on/off."""
        if self.is_recording:
            self.stop_dictation()
        else:
            self.start_dictation()
    
    def start_dictation(self):
        """Start dictation."""
        # #region agent log
        _debug_log("debug-session", "run1", "H4", "main.py:start_dictation:entry", "start_dictation called", {"is_recording": self.is_recording, "is_processing": self.is_processing})
        # #endregion
        if self.is_recording or self.is_processing:
            print("Already recording or processing, ignoring start request")
            # #region agent log
            _debug_log("debug-session", "run1", "H4", "main.py:start_dictation:early_return", "Early return - already recording/processing")
            # #endregion
            return
        
        try:
            print("Starting dictation...")
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "main.py:start_dictation:before_set", "Before setting is_recording", {"audio_chunks_count": len(self.audio_chunks)})
            # #endregion
            self.is_recording = True
            self.audio_chunks = []
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "main.py:start_dictation:after_set", "After setting is_recording", {"is_recording": self.is_recording, "audio_chunks_cleared": True})
            # #endregion
            
            # Start audio capture
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "main.py:start_dictation:before_audio_start", "Before audio_capture.start_recording", {"device_id": self.audio_capture.device_id})
            # #endregion
            audio_start_result = self.audio_capture.start_recording()
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "main.py:start_dictation:after_audio_start", "After audio_capture.start_recording", {"result": audio_start_result, "is_recording": self.audio_capture.is_recording})
            # #endregion
            if not audio_start_result:
                print("Failed to start audio capture")
                # #region agent log
                _debug_log("debug-session", "run1", "H2", "main.py:start_dictation:audio_failed", "Audio capture failed to start")
                # #endregion
                from PyQt6.QtWidgets import QSystemTrayIcon
                self.show_message_signal.emit(
                    "VocalNode",
                    "Failed to start audio capture. Check microphone permissions.",
                    QSystemTrayIcon.MessageIcon.Warning
                )
                self.is_recording = False
                return
            
            print("Audio capture started successfully")
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "main.py:start_dictation:audio_success", "Audio capture started successfully")
            # #endregion
            
            # Show overlay
            overlay_enabled = self.config.get("overlay.enabled", True)
            if overlay_enabled:
                self.overlay.set_listening(True)
            
            # Update tray icon
            self.tray_icon.update_state(True, False)
            
            # Start recording thread
            # #region agent log
            _debug_log("debug-session", "run1", "H6", "main.py:start_dictation:before_thread", "Before starting recording thread")
            # #endregion
            self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
            self.recording_thread.start()
            # #region agent log
            _debug_log("debug-session", "run1", "H6", "main.py:start_dictation:thread_started", "Recording thread started", {"thread_alive": self.recording_thread.is_alive()})
            # #endregion
            
        except Exception as e:
            print(f"Error starting dictation: {e}")
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "main.py:start_dictation:exception", "Exception in start_dictation", {"error": str(e), "type": type(e).__name__})
            # #endregion
            self.is_recording = False
            self.audio_capture.stop_recording()
    
    def stop_dictation(self):
        """Stop dictation and process audio."""
        # #region agent log
        _debug_log("debug-session", "run1", "H2", "main.py:stop_dictation:entry", "stop_dictation called", {"is_recording": self.is_recording})
        # #endregion
        if not self.is_recording:
            print("Not recording, ignoring stop request")
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "main.py:stop_dictation:early_return", "Early return - not recording")
            # #endregion
            return
        
        print("Stopping dictation...")
        # #region agent log
        _debug_log("debug-session", "run1", "H2", "main.py:stop_dictation:before_stop", "Before stopping", {"audio_chunks_count": len(self.audio_chunks), "queue_size": self.audio_capture.audio_queue.qsize() if hasattr(self.audio_capture, 'audio_queue') else 'N/A'})
        # #endregion
        self.is_recording = False
        self.is_processing = True
        # #region agent log
        _debug_log("debug-session", "run1", "H2", "main.py:stop_dictation:after_stop", "After stopping", {"is_recording": self.is_recording, "is_processing": self.is_processing})
        # #endregion
        
        # Reset hotkey pressed state for toggle mode
        if self.hotkey_manager.mode == "toggle":
            self.hotkey_manager.is_pressed = False
        
        # Stop audio capture
        # #region agent log
        _debug_log("debug-session", "run1", "H2", "main.py:stop_dictation:before_audio_stop", "Before audio_capture.stop_recording", {"audio_chunks_before": len(self.audio_chunks)})
        # #endregion
        self.audio_capture.stop_recording()
        print(f"Collected {len(self.audio_chunks)} audio chunks")
        # #region agent log
        _debug_log("debug-session", "run1", "H2", "main.py:stop_dictation:after_audio_stop", "After audio_capture.stop_recording", {"audio_chunks_after": len(self.audio_chunks), "audio_capture_is_recording": self.audio_capture.is_recording})
        # #endregion
        
        # Update overlay
        self.overlay.set_listening(False)
        self.overlay.set_text("Processing...")
        
        # Update tray icon
        self.tray_icon.update_state(False, True)
        
        # Process audio in background
        # #region agent log
        _debug_log("debug-session", "run1", "H3", "main.py:stop_dictation:before_process_thread", "Before starting processing thread")
        # #endregion
        processing_thread = threading.Thread(target=self._process_audio, daemon=True)
        processing_thread.start()
        # #region agent log
        _debug_log("debug-session", "run1", "H3", "main.py:stop_dictation:process_thread_started", "Processing thread started", {"thread_alive": processing_thread.is_alive()})
        # #endregion
    
    def _recording_loop(self):
        """Main recording loop - collects audio chunks."""
        # #region agent log
        _debug_log("debug-session", "run1", "H6", "main.py:_recording_loop:entry", "Recording loop started", {"is_recording": self.is_recording})
        # #endregion
        loop_count = 0
        chunks_collected = 0
        while self.is_recording:
            loop_count += 1
            # #region agent log
            if loop_count % 10 == 0:  # Log every 10 iterations to avoid spam
                _debug_log("debug-session", "run1", "H6", "main.py:_recording_loop:iteration", "Recording loop iteration", {"loop_count": loop_count, "chunks_collected": chunks_collected, "is_recording": self.is_recording})
            # #endregion
            chunk = self.audio_capture.get_audio_chunk(timeout=0.5)
            if chunk is not None:
                chunks_collected += 1
                # #region agent log
                _debug_log("debug-session", "run1", "H6", "main.py:_recording_loop:chunk_received", "Chunk received", {"chunk_size": len(chunk), "chunks_collected": chunks_collected})
                # #endregion
                self.audio_chunks.append(chunk)
            time.sleep(0.1)
        # #region agent log
        _debug_log("debug-session", "run1", "H6", "main.py:_recording_loop:exit", "Recording loop exited", {"total_iterations": loop_count, "total_chunks": chunks_collected, "final_chunks_count": len(self.audio_chunks)})
        # #endregion
    
    def _process_audio(self):
        """Process recorded audio and insert text."""
        # #region agent log
        _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:entry", "Processing audio started", {"audio_chunks_count": len(self.audio_chunks)})
        # #endregion
        try:
            import numpy as np
            
            # Get audio from queue first (most reliable)
            # #region agent log
            _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:before_get_audio", "Before get_all_audio", {"queue_size": self.audio_capture.audio_queue.qsize() if hasattr(self.audio_capture, 'audio_queue') else 'N/A'})
            # #endregion
            audio = self.audio_capture.get_all_audio()
            # #region agent log
            _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:after_get_audio", "After get_all_audio", {"audio_length": len(audio), "audio_dtype": str(audio.dtype) if len(audio) > 0 else "empty"})
            # #endregion
            
            # Fallback: use collected chunks if queue is empty
            if len(audio) == 0 and self.audio_chunks:
                print(f"Using fallback: {len(self.audio_chunks)} chunks")
                # #region agent log
                _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:using_fallback", "Using fallback chunks", {"chunks_count": len(self.audio_chunks)})
                # #endregion
                audio = np.concatenate(self.audio_chunks) if self.audio_chunks else np.array([], dtype=np.float32)
                # #region agent log
                _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:after_fallback", "After fallback concatenation", {"audio_length": len(audio)})
                # #endregion
            
            print(f"Processing audio: {len(audio)} samples, duration: {len(audio)/16000:.2f}s")
            # #region agent log
            _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:audio_ready", "Audio ready for processing", {"samples": len(audio), "duration_sec": len(audio)/16000 if len(audio) > 0 else 0})
            # #endregion
            
            if len(audio) == 0:
                print("No audio data to process")
                self.processing_done.emit()
                return
            
            # Ensure minimum audio length (at least 0.5 seconds)
            if len(audio) < 8000:  # Less than 0.5 seconds at 16kHz
                print(f"Audio too short: {len(audio)} samples")
                self.processing_done.emit()
                return
            
            # Transcribe
            sample_rate = self.config.get("audio.sample_rate", 16000)
            print(f"Transcribing audio with sample rate: {sample_rate}")
            # #region agent log
            _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:before_transcribe", "Before transcription", {"sample_rate": sample_rate, "audio_shape": audio.shape if len(audio) > 0 else "empty", "audio_max": float(np.max(np.abs(audio))) if len(audio) > 0 else 0})
            # #endregion
            text = self.stt_engine.transcribe_audio(audio, sample_rate)
            print(f"Transcribed text: '{text}'")
            # #region agent log
            _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:after_transcribe", "After transcription", {"text": text, "text_length": len(text) if text else 0})
            # #endregion
            
            # Update overlay with transcribed text
            overlay_enabled = self.config.get("overlay.enabled", True)
            if overlay_enabled:
                self.overlay.set_text(text)
            
            # Insert text into active window
            if text and text.strip():
                print(f"Inserting text: '{text[:50]}...'")
                # #region agent log
                _debug_log("debug-session", "run1", "H4", "main.py:_process_audio:before_emit_text", "Before emitting text_ready signal", {"text_preview": text[:50]})
                # #endregion
                # Emit signal to run on main thread
                self.text_ready.emit(text)
                # #region agent log
                _debug_log("debug-session", "run1", "H4", "main.py:_process_audio:after_emit_text", "After emitting text_ready signal")
                # #endregion
            else:
                print("No text transcribed or empty text")
                # #region agent log
                _debug_log("debug-session", "run1", "H3", "main.py:_process_audio:no_text", "No text to insert", {"text": text, "text_is_empty": not (text and text.strip())})
                # #endregion
                self.processing_done.emit()
        
        except Exception as e:
            print(f"Error processing audio: {e}")
            from PyQt6.QtWidgets import QSystemTrayIcon
            self.show_message_signal.emit(
                "VocalNode",
                f"Error processing audio: {e}",
                QSystemTrayIcon.MessageIcon.Critical
            )
            self.processing_done.emit()
    
    def _insert_text(self, text: str):
        """Insert text into active window (runs on main thread)."""
        # #region agent log
        _debug_log("debug-session", "run1", "H4", "main.py:_insert_text:entry", "Text insertion handler called", {"text_length": len(text), "text_preview": text[:50]})
        # #endregion
        from PyQt6.QtWidgets import QSystemTrayIcon
        # #region agent log
        _debug_log("debug-session", "run1", "H5", "main.py:_insert_text:before_insert", "Before text_inserter.insert_text", {"method": self.text_inserter.method})
        # #endregion
        success = self.text_inserter.insert_text(text)
        # #region agent log
        _debug_log("debug-session", "run1", "H5", "main.py:_insert_text:after_insert", "After text_inserter.insert_text", {"success": success})
        # #endregion
        if success:
            self.tray_icon.show_message(
                "VocalNode",
                f"Inserted: {text[:50]}...",
                QSystemTrayIcon.MessageIcon.Information
            )
        else:
            self.tray_icon.show_message(
                "VocalNode",
                "Failed to insert text",
                QSystemTrayIcon.MessageIcon.Warning
            )
        self.processing_done.emit()
    
    def _on_processing_done(self):
        """Handle processing completion (runs on main thread)."""
        # #region agent log
        _debug_log("debug-session", "run1", "H4", "main.py:_on_processing_done:entry", "Processing done handler called")
        # #endregion
        self.is_processing = False
        self.tray_icon.update_state(False, False)
        overlay_enabled = self.config.get("overlay.enabled", True)
        if overlay_enabled:
            QTimer.singleShot(2000, self.overlay.hide_overlay)
        # #region agent log
        _debug_log("debug-session", "run1", "H4", "main.py:_on_processing_done:exit", "Processing done handler completed", {"is_processing": self.is_processing})
        # #endregion
    
    def quit_application(self):
        """Quit the application."""
        self.hotkey_manager.stop()
        self.audio_capture.stop_recording()
        QApplication.quit()


def main():
    """Main entry point."""
    # Check if system tray is available
    app = QApplication(sys.argv)
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("System tray is not available on this system.")
        sys.exit(1)
    
    app.setQuitOnLastWindowClosed(False)
    
    # Create and run application
    vocal_node = VocalNodeApp()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


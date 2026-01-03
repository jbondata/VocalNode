"""Text insertion into active window."""

import time
import json
from typing import Optional
from pynput import keyboard
from pynput.keyboard import Key, Controller

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


class TextInserter:
    """Handles inserting transcribed text into the active window."""
    
    def __init__(self, config):
        """Initialize text inserter.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.keyboard = Controller()
        self.typing_delay = config.get("text_insertion.typing_delay", 0.01)
        self.method = config.get("text_insertion.method", "typing")
    
    def insert_text(self, text: str) -> bool:
        """Insert text into the active window.
        
        Args:
            text: Text to insert
            
        Returns:
            True if successful, False otherwise
        """
        # #region agent log
        _debug_log("debug-session", "run1", "H5", "text_inserter.py:insert_text:entry", "insert_text called", {"text_length": len(text), "method": self.method, "text_preview": text[:50]})
        # #endregion
        if not text or not text.strip():
            # #region agent log
            _debug_log("debug-session", "run1", "H5", "text_inserter.py:insert_text:empty", "Text is empty, returning False")
            # #endregion
            return False
        
        try:
            if self.method == "clipboard":
                # #region agent log
                _debug_log("debug-session", "run1", "H5", "text_inserter.py:insert_text:clipboard", "Using clipboard method")
                # #endregion
                return self._insert_via_clipboard(text)
            else:
                # #region agent log
                _debug_log("debug-session", "run1", "H5", "text_inserter.py:insert_text:typing", "Using typing method")
                # #endregion
                return self._insert_via_typing(text)
        except Exception as e:
            print(f"Error inserting text: {e}")
            # #region agent log
            _debug_log("debug-session", "run1", "H5", "text_inserter.py:insert_text:exception", "Exception in insert_text", {"error": str(e), "type": type(e).__name__})
            # #endregion
            return False
    
    def _insert_via_typing(self, text: str) -> bool:
        """Insert text by simulating keyboard typing.
        
        Args:
            text: Text to type
            
        Returns:
            True if successful
        """
        # #region agent log
        _debug_log("debug-session", "run1", "H5", "text_inserter.py:_insert_via_typing:entry", "Typing method started", {"text_length": len(text), "typing_delay": self.typing_delay})
        # #endregion
        try:
            chars_typed = 0
            # Type character by character with small delay
            for char in text:
                chars_typed += 1
                if char == '\n':
                    self.keyboard.press(Key.enter)
                    self.keyboard.release(Key.enter)
                elif char == '\t':
                    self.keyboard.press(Key.tab)
                    self.keyboard.release(Key.tab)
                else:
                    self.keyboard.type(char)
                time.sleep(self.typing_delay)
            # #region agent log
            _debug_log("debug-session", "run1", "H5", "text_inserter.py:_insert_via_typing:success", "Typing completed", {"chars_typed": chars_typed})
            # #endregion
            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            # #region agent log
            _debug_log("debug-session", "run1", "H5", "text_inserter.py:_insert_via_typing:exception", "Exception in typing", {"error": str(e), "type": type(e).__name__, "chars_typed": chars_typed})
            # #endregion
            return False
    
    def _insert_via_clipboard(self, text: str) -> bool:
        """Insert text via clipboard paste.
        
        Args:
            text: Text to paste
            
        Returns:
            True if successful
        """
        try:
            import pyperclip
            
            # Save current clipboard
            try:
                old_clipboard = pyperclip.paste()
            except:
                old_clipboard = None
            
            # Copy text to clipboard
            pyperclip.copy(text)
            
            # Paste using Ctrl+V (Windows/Linux) or Cmd+V (macOS)
            import platform
            if platform.system() == "Darwin":  # macOS
                with self.keyboard.pressed(Key.cmd):
                    self.keyboard.press('v')
                    self.keyboard.release('v')
            else:  # Windows/Linux
                with self.keyboard.pressed(Key.ctrl):
                    self.keyboard.press('v')
                    self.keyboard.release('v')
            
            # Restore old clipboard after a delay
            time.sleep(0.1)
            if old_clipboard is not None:
                try:
                    pyperclip.copy(old_clipboard)
                except:
                    pass
            
            return True
        except ImportError:
            print("pyperclip not installed, falling back to typing method")
            return self._insert_via_typing(text)
        except Exception as e:
            print(f"Error pasting text: {e}")
            return False


"""Global hotkey management."""

import platform
import threading
import json
import time
import os
from typing import Optional, Callable
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

# Detect Wayland
IS_WAYLAND = os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland'

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


class HotkeyManager:
    """Manages global hotkey registration and handling."""
    
    def __init__(self, config, on_press: Optional[Callable] = None, 
                 on_release: Optional[Callable] = None):
        """Initialize hotkey manager.
        
        Args:
            config: Configuration object
            on_press: Callback when hotkey is pressed
            on_release: Callback when hotkey is released
        """
        self.config = config
        self.on_press = on_press
        self.on_release = on_release
        self.listener: Optional[keyboard.Listener] = None
        self.is_pressed = False
        self.mode = config.get("hotkey.mode", "toggle")
        self.hotkey_key = None
        self.hotkey_modifiers = []
        self.pressed_modifiers = set()
        self._load_hotkey()
    
    def _load_hotkey(self):
        """Load hotkey configuration."""
        key_str = self.config.get("hotkey.key", "f8")
        modifiers = self.config.get("hotkey.modifiers", [])
        
        # Parse key
        try:
            key_lower = key_str.lower()
            # Map special keys to Key enum
            key_map = {
                'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
                'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
                'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
                'space': Key.space, 'insert': Key.insert, 'delete': Key.delete,
                'home': Key.home, 'end': Key.end, 'page_up': Key.page_up,
                'page_down': Key.page_down, 'up': Key.up, 'down': Key.down,
                'left': Key.left, 'right': Key.right, 'enter': Key.enter,
                'return': Key.enter, 'tab': Key.tab, 'backspace': Key.backspace,
                'escape': Key.esc
            }
            
            if key_lower in key_map:
                self.hotkey_key = key_map[key_lower]
            elif hasattr(Key, key_lower):
                # Try direct attribute access
                self.hotkey_key = getattr(Key, key_lower)
            elif len(key_lower) == 1:
                # Single character key (a-z, 0-9, etc.)
                self.hotkey_key = KeyCode.from_char(key_lower)
            else:
                # Try to find by name
                try:
                    # Convert to Key enum if possible
                    key_attr = key_lower.replace('_', '')
                    if hasattr(Key, key_attr):
                        self.hotkey_key = getattr(Key, key_attr)
                    else:
                        # Fallback: try as character
                        self.hotkey_key = KeyCode.from_char(key_lower[0])
                except:
                    self.hotkey_key = KeyCode.from_char(key_lower[0] if key_lower else 'f8')
            
            print(f"Loaded hotkey: {key_str} -> {self.hotkey_key}")
        except Exception as e:
            print(f"Error loading hotkey '{key_str}': {e}")
            self.hotkey_key = Key.f8  # Default
        
        # Parse modifiers
        self.hotkey_modifiers = []
        for mod in modifiers:
            mod_lower = mod.lower()
            if mod_lower == "ctrl" or mod_lower == "control":
                self.hotkey_modifiers.append(Key.ctrl)
            elif mod_lower == "alt":
                self.hotkey_modifiers.append(Key.alt)
            elif mod_lower == "shift":
                self.hotkey_modifiers.append(Key.shift)
            elif mod_lower == "cmd" or mod_lower == "meta":
                self.hotkey_modifiers.append(Key.cmd)
    
    def _check_modifiers(self) -> bool:
        """Check if required modifiers are pressed.
        
        Returns:
            True if all required modifiers are pressed
        """
        if not self.hotkey_modifiers:
            return True
        
        # Check if all required modifiers are in pressed set
        return all(mod in self.pressed_modifiers for mod in self.hotkey_modifiers)
    
    def _on_press(self, key):
        """Handle key press event."""
        # Log ALL key presses to verify listener is working
        # #region agent log
        _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:_on_press:entry", "Key press event received", {"key": str(key), "key_type": type(key).__name__, "hotkey_key": str(self.hotkey_key), "hotkey_key_type": type(self.hotkey_key).__name__, "is_pressed": self.is_pressed, "mode": self.mode, "is_wayland": IS_WAYLAND})
        # #endregion
        # Also print to console for immediate visibility
        print(f"[HOTKEY DEBUG] Key pressed: {key} (listener is receiving events!)")
        try:
            # Track modifier keys
            if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r, Key.alt, Key.alt_l, Key.alt_r,
                      Key.shift, Key.shift_l, Key.shift_r, Key.cmd, Key.cmd_l, Key.cmd_r]:
                # #region agent log
                _debug_log("debug-session", "run1", "H7", "hotkey_manager.py:_on_press:modifier", "Modifier key detected", {"key": str(key)})
                # #endregion
                if key == Key.ctrl_l or key == Key.ctrl_r:
                    self.pressed_modifiers.add(Key.ctrl)
                elif key == Key.alt_l or key == Key.alt_r:
                    self.pressed_modifiers.add(Key.alt)
                elif key == Key.shift_l or key == Key.shift_r:
                    self.pressed_modifiers.add(Key.shift)
                elif key == Key.cmd_l or key == Key.cmd_r:
                    self.pressed_modifiers.add(Key.cmd)
                else:
                    self.pressed_modifiers.add(key)
            
            # Check if this is our hotkey key
            # Handle both Key enum and KeyCode comparison
            key_matches = False
            if isinstance(self.hotkey_key, Key) and isinstance(key, Key):
                key_matches = (key == self.hotkey_key)
                # #region agent log
                _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:_on_press:key_match_check", "Key match check (Key vs Key)", {"key": str(key), "hotkey_key": str(self.hotkey_key), "matches": key_matches})
                # #endregion
            elif isinstance(self.hotkey_key, KeyCode) and isinstance(key, KeyCode):
                key_matches = (key.char == self.hotkey_key.char if hasattr(key, 'char') and hasattr(self.hotkey_key, 'char') else key == self.hotkey_key)
                # #region agent log
                _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:_on_press:keycode_match_check", "Key match check (KeyCode vs KeyCode)", {"key_char": getattr(key, 'char', None), "hotkey_char": getattr(self.hotkey_key, 'char', None), "matches": key_matches})
                # #endregion
            else:
                # Try direct comparison
                key_matches = (key == self.hotkey_key)
                # #region agent log
                _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:_on_press:direct_match_check", "Key match check (direct)", {"matches": key_matches, "key_type": type(key).__name__, "hotkey_type": type(self.hotkey_key).__name__})
                # #endregion
            
            if key_matches:
                # #region agent log
                _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:_on_press:key_matched", "Key matched!", {"pressed_modifiers": list(self.pressed_modifiers), "required_modifiers": [str(m) for m in self.hotkey_modifiers]})
                # #endregion
                # Check if modifiers match (if any required)
                modifiers_match = self._check_modifiers()
                # #region agent log
                _debug_log("debug-session", "run1", "H7", "hotkey_manager.py:_on_press:modifier_check", "Modifier check result", {"modifiers_match": modifiers_match, "pressed": list(self.pressed_modifiers), "required": [str(m) for m in self.hotkey_modifiers]})
                # #endregion
                if modifiers_match:
                    if self.mode == "hold":
                        if not self.is_pressed:
                            self.is_pressed = True
                            print(f"Hotkey pressed (hold mode): {key}")
                            if self.on_press:
                                self.on_press()
                    else:  # toggle mode
                        # Toggle state - if not pressed, start; if pressed, stop
                        if not self.is_pressed:
                            self.is_pressed = True
                            print(f"Hotkey pressed (toggle mode - start): {key}")
                            # #region agent log
                            _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:_on_press:toggle_start", "Toggle mode - calling on_press", {"on_press_exists": self.on_press is not None})
                            # #endregion
                            if self.on_press:
                                self.on_press()
                                # #region agent log
                                _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:_on_press:on_press_called", "on_press callback executed")
                                # #endregion
                        else:
                            # In toggle mode, pressing again stops
                            self.is_pressed = False
                            print(f"Hotkey pressed (toggle mode - stop): {key}")
                            if self.on_release:
                                self.on_release()
        except Exception as e:
            print(f"Error in hotkey press handler: {e}")
    
    def _on_release(self, key):
        """Handle key release event."""
        try:
            # Remove modifier from pressed set
            if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r, Key.alt, Key.alt_l, Key.alt_r,
                       Key.shift, Key.shift_l, Key.shift_r, Key.cmd, Key.cmd_l, Key.cmd_r]:
                if key == Key.ctrl_l or key == Key.ctrl_r:
                    self.pressed_modifiers.discard(Key.ctrl)
                elif key == Key.alt_l or key == Key.alt_r:
                    self.pressed_modifiers.discard(Key.alt)
                elif key == Key.shift_l or key == Key.shift_r:
                    self.pressed_modifiers.discard(Key.shift)
                elif key == Key.cmd_l or key == Key.cmd_r:
                    self.pressed_modifiers.discard(Key.cmd)
                else:
                    self.pressed_modifiers.discard(key)
            
            # Handle hotkey release
            # Use same matching logic as press handler
            key_matches = False
            if isinstance(self.hotkey_key, Key) and isinstance(key, Key):
                key_matches = (key == self.hotkey_key)
            elif isinstance(self.hotkey_key, KeyCode) and isinstance(key, KeyCode):
                key_matches = (key.char == self.hotkey_key.char if hasattr(key, 'char') and hasattr(self.hotkey_key, 'char') else key == self.hotkey_key)
            else:
                key_matches = (key == self.hotkey_key)
            
            if key_matches:
                if self.mode == "hold":
                    if self.is_pressed:
                        self.is_pressed = False
                        if self.on_release:
                            self.on_release()
                # In toggle mode, release doesn't stop recording
        except Exception as e:
            print(f"Error in hotkey release handler: {e}")
    
    def start(self) -> bool:
        """Start listening for hotkeys.
        
        Returns:
            True if started successfully
        """
        # #region agent log
        _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:start:entry", "Starting hotkey listener", {"listener_exists": self.listener is not None, "hotkey_key": str(self.hotkey_key), "hotkey_modifiers": [str(m) for m in self.hotkey_modifiers], "is_wayland": IS_WAYLAND})
        # #endregion
        
        if IS_WAYLAND:
            # #region agent log
            _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:start:wayland_detected", "Wayland detected - pynput may not work", {"session_type": os.environ.get('XDG_SESSION_TYPE', 'unknown')})
            # #endregion
            print("WARNING: Wayland detected. pynput keyboard listener may not work properly.")
            print("Consider using X11 or installing 'keyboard' library for better Wayland support.")
        
        if self.listener is not None:
            # #region agent log
            _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:start:already_running", "Listener already running")
            # #endregion
            return False
        
        try:
            # #region agent log
            _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:start:before_listener", "Before creating keyboard.Listener", {"is_wayland": IS_WAYLAND})
            # #endregion
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
                suppress=False  # Don't suppress keys, just listen
            )
            # #region agent log
            _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:start:listener_created", "Listener created, starting")
            # #endregion
            self.listener.start()
            # #region agent log
            _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:start:listener_started", "Listener started", {"listener_alive": self.listener.is_alive(), "listener_running": self.listener.running if hasattr(self.listener, 'running') else 'unknown'})
            # #endregion
            # Verify listener is actually running after a brief moment
            time.sleep(0.2)  # Give it more time
            # #region agent log
            _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:start:listener_verified", "Listener verified", {"listener_alive": self.listener.is_alive(), "listener_running": self.listener.running if hasattr(self.listener, 'running') else 'unknown', "is_wayland": IS_WAYLAND})
            # #endregion
            
            # Test if listener is actually receiving events
            if IS_WAYLAND:
                print("NOTE: On Wayland, you may need to:")
                print("  1. Install 'keyboard' library: pip install keyboard")
                print("  2. Or switch to X11 session")
                print("  3. Or use the tray icon menu to start/stop dictation")
            
            return True
        except Exception as e:
            print(f"Error starting hotkey listener: {e}")
            # #region agent log
            _debug_log("debug-session", "run1", "H1", "hotkey_manager.py:start:exception", "Exception starting listener", {"error": str(e), "type": type(e).__name__, "is_wayland": IS_WAYLAND})
            # #endregion
            return False
    
    def set_hotkey(self, key: str, modifiers: list = None, mode: str = "toggle"):
        """Set new hotkey configuration.
        
        Args:
            key: Key name (e.g., "f8")
            modifiers: List of modifier keys (e.g., ["ctrl", "shift"])
            mode: "toggle" or "hold"
        """
        self.config.set("hotkey.key", key)
        self.config.set("hotkey.modifiers", modifiers or [])
        self.config.set("hotkey.mode", mode)
        self.mode = mode
        self._load_hotkey()
    
    def toggle_recording(self):
        """Manually toggle recording (for toggle mode)."""
        if self.mode == "toggle":
            if self.is_pressed:
                self.is_pressed = False
                if self.on_release:
                    self.on_release()
            else:
                self.is_pressed = True
                if self.on_press:
                    self.on_press()
    
    def stop(self):
        """Stop listening for hotkeys."""
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        self.pressed_modifiers.clear()
        self.is_pressed = False


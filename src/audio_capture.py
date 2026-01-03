"""Audio capture from microphone."""

import queue
import threading
import json
import time
import sounddevice as sd
import numpy as np
from typing import Optional, Callable

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


class AudioCapture:
    """Captures audio from microphone in real-time."""
    
    def __init__(self, config, sample_rate: int = 16000, channels: int = 1):
        """Initialize audio capture.
        
        Args:
            config: Configuration object
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
        """
        self.config = config
        self.sample_rate = sample_rate
        self.channels = channels
        self.device_id = config.get("audio.device_id")
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream: Optional[sd.InputStream] = None
        self.callback: Optional[Callable] = None
        self._callback_count = 0  # For debug logging
    
    def list_devices(self) -> list:
        """List available audio input devices.
        
        Returns:
            List of device dictionaries
        """
        devices = sd.query_devices()
        input_devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'id': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        return input_devices
    
    def start_recording(self, callback: Optional[Callable] = None) -> bool:
        """Start recording audio.
        
        Args:
            callback: Optional callback function for audio chunks
            
        Returns:
            True if started successfully
        """
        if self.is_recording:
            return False
        
        self.callback = callback
        self.is_recording = True
        
        try:
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "audio_capture.py:start_recording:before_stream", "Before creating InputStream", {"device_id": self.device_id, "channels": self.channels, "sample_rate": self.sample_rate})
            # #endregion
            self.stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=np.float32,
                callback=self._audio_callback,
                blocksize=int(self.sample_rate * 0.5)  # 0.5 second blocks
            )
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "audio_capture.py:start_recording:stream_created", "InputStream created, starting stream")
            # #endregion
            self.stream.start()
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "audio_capture.py:start_recording:stream_started", "Stream started successfully", {"stream_active": self.stream.active})
            # #endregion
            return True
        except Exception as e:
            print(f"Error starting audio capture: {e}")
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "audio_capture.py:start_recording:exception", "Exception starting audio capture", {"error": str(e), "type": type(e).__name__})
            # #endregion
            self.is_recording = False
            return False
    
    def stop_recording(self) -> None:
        """Stop recording audio."""
        self.is_recording = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            self.stream = None
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback function for audio stream."""
        # #region agent log
        callback_count = getattr(self, '_callback_count', 0) + 1
        self._callback_count = callback_count
        if callback_count % 20 == 0:  # Log every 20th callback to avoid spam
            _debug_log("debug-session", "run1", "H2", "audio_capture.py:_audio_callback:entry", "Audio callback", {"callback_count": callback_count, "is_recording": self.is_recording, "frames": frames, "queue_size": self.audio_queue.qsize()})
        # #endregion
        if status:
            print(f"Audio callback status: {status}")
            # #region agent log
            _debug_log("debug-session", "run1", "H2", "audio_capture.py:_audio_callback:status", "Audio callback status", {"status": str(status)})
            # #endregion
        
        if self.is_recording:
            # Convert to mono if stereo
            audio_data = indata[:, 0] if indata.ndim > 1 else indata
            # #region agent log
            if callback_count % 20 == 0:
                _debug_log("debug-session", "run1", "H2", "audio_capture.py:_audio_callback:processing", "Processing audio data", {"audio_shape": audio_data.shape, "audio_max": float(np.max(np.abs(audio_data)))})
            # #endregion
            
            # Put in queue for processing
            try:
                self.audio_queue.put_nowait(audio_data.copy())
                # #region agent log
                if callback_count % 20 == 0:
                    _debug_log("debug-session", "run1", "H2", "audio_capture.py:_audio_callback:queued", "Audio data queued", {"queue_size": self.audio_queue.qsize()})
                # #endregion
            except queue.Full:
                # #region agent log
                _debug_log("debug-session", "run1", "H2", "audio_capture.py:_audio_callback:queue_full", "Queue full, dropping frame")
                # #endregion
                pass  # Drop frame if queue is full
            
            # Call user callback if provided
            if self.callback:
                try:
                    self.callback(audio_data)
                except Exception as e:
                    print(f"Error in audio callback: {e}")
    
    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """Get next audio chunk from queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Audio chunk as numpy array or None
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_all_audio(self) -> np.ndarray:
        """Get all buffered audio as single array.
        
        Returns:
            Concatenated audio array
        """
        chunks = []
        queue_size = self.audio_queue.qsize()
        print(f"Audio queue size: {queue_size}")
        
        while True:
            try:
                chunk = self.audio_queue.get_nowait()
                chunks.append(chunk)
            except queue.Empty:
                break
        
        if chunks:
            total_samples = sum(len(chunk) for chunk in chunks)
            print(f"Retrieved {len(chunks)} chunks from queue, total samples: {total_samples}")
            return np.concatenate(chunks)
        
        print("No audio chunks in queue")
        return np.array([], dtype=np.float32)


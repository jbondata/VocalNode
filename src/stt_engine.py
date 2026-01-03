"""Speech-to-text engine using faster-whisper."""

import os
import threading
from pathlib import Path
from typing import Optional, Callable
import numpy as np
from faster_whisper import WhisperModel


class STTEngine:
    """Speech-to-text engine using faster-whisper."""
    
    def __init__(self, config):
        """Initialize STT engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.model_name = config.get("stt.model", "base")
        self.language = config.get("stt.language", "en")
        self.device = config.get("stt.device", "cpu")
        self.model: Optional[WhisperModel] = None
        self.model_lock = threading.Lock()
        self.models_dir = Path.home() / ".vocalnode" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def load_model(self) -> bool:
        """Load the Whisper model.
        
        Returns:
            True if loaded successfully
        """
        if self.model is not None:
            return True
        
        try:
            print(f"Loading Whisper model: {self.model_name} (device: {self.device})")
            
            # Use local cache directory
            model_path = str(self.models_dir / self.model_name)
            
            # Download model if not exists
            if not os.path.exists(model_path):
                print(f"Downloading model {self.model_name}...")
            
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type="int8",  # Use int8 for faster inference
                download_root=str(self.models_dir)
            )
            
            print("Model loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def transcribe_audio(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio to text.
        
        Args:
            audio: Audio array (numpy array of floats)
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text
        """
        if self.model is None:
            if not self.load_model():
                return ""
        
        try:
            with self.model_lock:
                # Ensure audio is float32 and normalized
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)
                
                # Normalize audio
                if np.max(np.abs(audio)) > 0:
                    audio = audio / np.max(np.abs(audio))
                
                # Transcribe
                segments, info = self.model.transcribe(
                    audio,
                    language=self.language if self.language != "auto" else None,
                    beam_size=5,
                    vad_filter=True,  # Voice activity detection
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                
                # Collect text from segments
                text_parts = []
                for segment in segments:
                    text_parts.append(segment.text.strip())
                
                text = " ".join(text_parts).strip()
                return text
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""
    
    def transcribe_stream(self, audio_chunks: list, sample_rate: int = 16000) -> str:
        """Transcribe a stream of audio chunks.
        
        Args:
            audio_chunks: List of audio chunks (numpy arrays)
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text
        """
        if not audio_chunks:
            return ""
        
        # Concatenate all chunks
        audio = np.concatenate(audio_chunks)
        return self.transcribe_audio(audio, sample_rate)
    
    def set_language(self, language: str) -> None:
        """Set transcription language.
        
        Args:
            language: Language code (e.g., "en", "es", "fr")
        """
        self.language = language
        self.config.set("stt.language", language)
    
    def set_model(self, model_name: str) -> bool:
        """Change the model.
        
        Args:
            model_name: Model name (tiny, base, small, medium, large)
            
        Returns:
            True if model changed successfully
        """
        if model_name == self.model_name:
            return True
        
        self.model_name = model_name
        self.config.set("stt.model", model_name)
        self.model = None  # Force reload
        return self.load_model()


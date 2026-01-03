"""Dictation overlay window with visual feedback."""

import sys
import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from typing import Optional


class DictationOverlay(QWidget):
    """Floating overlay window showing dictation status."""
    
    def __init__(self, config):
        """Initialize overlay window.
        
        Args:
            config: Configuration object
        """
        super().__init__()
        self.config = config
        self.is_listening = False
        self.current_text = ""
        self.animation_value = 0.0
        
        self.setup_ui()
        self.setup_animation()
        self.update_position()
    
    def setup_ui(self):
        """Setup the UI components."""
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Set size
        self.setFixedSize(300, 120)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Text preview label
        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                background: transparent;
            }
        """)
        self.text_label.setMaximumHeight(60)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)
        
        # Set opacity
        opacity = self.config.get("overlay.opacity", 0.9)
        self.setWindowOpacity(opacity)
    
    def setup_animation(self):
        """Setup pulsing animation."""
        self.animation = QPropertyAnimation(self, b"animationValue")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.setLoopCount(-1)  # Infinite loop
    
    def update_position(self):
        """Update overlay position based on config."""
        position = self.config.get("overlay.position", "bottom_right")
        
        # Get screen geometry
        screen = QApplication.primaryScreen().geometry()
        width = self.width()
        height = self.height()
        margin = 20
        
        if position == "top_left":
            x = margin
            y = margin
        elif position == "top_right":
            x = screen.width() - width - margin
            y = margin
        elif position == "bottom_left":
            x = margin
            y = screen.height() - height - margin
        elif position == "bottom_right":
            x = screen.width() - width - margin
            y = screen.height() - height - margin
        else:  # center
            x = (screen.width() - width) // 2
            y = (screen.height() - height) // 2
        
        self.move(x, y)
    
    def paintEvent(self, event):
        """Custom paint event for rounded background with animation."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background color based on state
        if self.is_listening:
            # Pulsing blue when listening
            base_alpha = 200
            pulse_alpha = int(50 * self.animation_value)
            alpha = min(255, base_alpha + pulse_alpha)
            bg_color = QColor(33, 150, 243, alpha)  # Blue
        else:
            bg_color = QColor(66, 66, 66, 200)  # Dark gray
        
        # Draw rounded rectangle background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # Draw waveform animation when listening
        if self.is_listening:
            self.draw_waveform(painter)
    
    def draw_waveform(self, painter):
        """Draw animated waveform indicator."""
        painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
        
        width = self.width()
        height = self.height()
        center_y = height // 2
        bar_width = 4
        bar_spacing = 6
        num_bars = 8
        
        start_x = (width - (num_bars * (bar_width + bar_spacing) - bar_spacing)) // 2
        
        for i in range(num_bars):
            # Animate bars with different phases
            phase = (i / num_bars) * 2 * 3.14159
            amplitude = 0.3 + 0.7 * abs(np.sin(self.animation_value * 2 * 3.14159 + phase))
            bar_height = int(20 * amplitude)
            
            x = start_x + i * (bar_width + bar_spacing)
            y = center_y - bar_height // 2
            
            painter.drawRect(x, y, bar_width, bar_height)
    
    def set_listening(self, listening: bool):
        """Set listening state.
        
        Args:
            listening: True if listening, False otherwise
        """
        self.is_listening = listening
        if listening:
            self.status_label.setText("Listening...")
            self.animation.start()
            self.show()
        else:
            self.status_label.setText("Processing...")
            self.animation.stop()
            self.animation_value = 0.0
        self.update()
    
    def set_text(self, text: str):
        """Set transcribed text preview.
        
        Args:
            text: Text to display
        """
        self.current_text = text
        show_text = self.config.get("overlay.show_text", True)
        if show_text and text:
            # Truncate if too long
            if len(text) > 50:
                text = text[:47] + "..."
            self.text_label.setText(text)
        else:
            self.text_label.setText("")
        self.update()
    
    def hide_overlay(self):
        """Hide the overlay."""
        self.hide()
        self.animation.stop()
        self.animation_value = 0.0
    
    def get_animation_value(self) -> float:
        """Get animation value for property animation."""
        return self.animation_value
    
    def set_animation_value(self, value: float):
        """Set animation value for property animation.
        
        Args:
            value: Animation value (0.0 to 1.0)
        """
        self.animation_value = value
        self.update()
    
    animationValue = pyqtProperty(float, get_animation_value, set_animation_value)


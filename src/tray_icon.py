"""System tray icon and menu."""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from typing import Optional


class TrayIcon(QObject):
    """System tray icon with context menu."""
    
    show_settings = pyqtSignal()
    toggle_dictation = pyqtSignal()
    quit_app = pyqtSignal()
    
    def __init__(self):
        """Initialize tray icon."""
        super().__init__()
        self.tray_icon = QSystemTrayIcon()
        self.setup_icon()
        self.setup_menu()
        self.tray_icon.setToolTip("VocalNode - Speech to Text")
        self.tray_icon.show()
    
    def setup_icon(self):
        """Setup the tray icon."""
        # Create a simple icon programmatically
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw microphone icon (simplified)
        painter.setBrush(QColor(66, 133, 244))  # Blue
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        
        # Draw microphone symbol
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        # Mic body
        painter.drawLine(16, 10, 16, 20)
        # Mic base
        painter.drawArc(12, 20, 8, 4, 0, 180 * 16)
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
    
    def setup_menu(self):
        """Setup context menu."""
        menu = QMenu()
        
        # Toggle dictation
        toggle_action = menu.addAction("Start Dictation")
        toggle_action.triggered.connect(self.toggle_dictation.emit)
        
        menu.addSeparator()
        
        # Settings
        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings.emit)
        
        menu.addSeparator()
        
        # Quit
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app.emit)
        
        self.tray_icon.setContextMenu(menu)
        self.menu = menu
        self.toggle_action = toggle_action
    
    def update_state(self, is_listening: bool, is_processing: bool = False):
        """Update icon and menu based on state.
        
        Args:
            is_listening: True if currently listening
            is_processing: True if processing audio
        """
        if is_listening:
            self.toggle_action.setText("Stop Dictation")
            self.tray_icon.setToolTip("VocalNode - Listening...")
            # Change icon color to green when listening
            self.set_listening_icon()
        elif is_processing:
            self.toggle_action.setText("Processing...")
            self.tray_icon.setToolTip("VocalNode - Processing...")
        else:
            self.toggle_action.setText("Start Dictation")
            self.tray_icon.setToolTip("VocalNode - Ready")
            self.set_idle_icon()
    
    def set_listening_icon(self):
        """Set icon to listening state (green)."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QColor(76, 175, 80))  # Green
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawLine(16, 10, 16, 20)
        painter.drawArc(12, 20, 8, 4, 0, 180 * 16)
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
    
    def set_idle_icon(self):
        """Set icon to idle state (blue)."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QColor(66, 133, 244))  # Blue
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawLine(16, 10, 16, 20)
        painter.drawArc(12, 20, 8, 4, 0, 180 * 16)
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
    
    def show_message(self, title: str, message: str, icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information):
        """Show a tray notification.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Icon type
        """
        self.tray_icon.showMessage(title, message, icon, 3000)


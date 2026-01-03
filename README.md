# VocalNode

A cross-platform speech-to-text dictation tool that works on Linux, Windows, and macOS. Similar to Whisper Flow, VocalNode allows you to freely hold or toggle a customizable keybind to dictate text into any active application window.

## Features

- **Cross-platform**: Works on Linux, Windows, and macOS
- **Offline**: Uses local Whisper models - no internet required, complete privacy
- **Global Hotkeys**: Customizable keybind that works across all applications
- **Visual Feedback**: Dictation overlay with animation showing listening status
- **Multiple Languages**: Support for 99+ languages
- **System Tray**: Minimal interface with system tray icon
- **Real-time**: Low-latency speech-to-text processing

## Installation

### Prerequisites

- Python 3.10 or higher
- A microphone/audio input device

### Install Dependencies

**Recommended: Use a virtual environment**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note for Arch Linux users:** You may need system dependencies:
```bash
sudo pacman -S portaudio python-evdev
```

### Verify Installation

```bash
./check_install.sh
```

### Run the Application

**Option 1: Using the launcher script (recommended)**
```bash
./start.sh
```

**Option 2: Manual start**
```bash
# Activate virtual environment first (if using venv)
source venv/bin/activate

# Run the application
python3 run.py
```

**Option 3: Direct module execution**
```bash
source venv/bin/activate
python3 -m src.main
```

## Usage

### Starting the Application

**Option 1: Using the launcher script**
```bash
cd /home/jb/dev/VocalNode
./start.sh
```

**Option 2: Manual start**
```bash
cd /home/jb/dev/VocalNode
source venv/bin/activate
python3 run.py
```

The application will appear in your system tray (look for the microphone icon).

### First-Time Setup

1. **Model Download**: On first run, the Whisper model will download automatically (~150MB for base model). You'll receive a notification when it's ready.

2. **Configure Settings**: Right-click the tray icon and select "Settings" to configure:
   - **Hotkey**: Set your preferred key (default: F8)
   - **Mode**: Choose "Toggle" (press to start/stop) or "Hold" (hold to record)
   - **Audio Device**: Select your microphone
   - **Language**: Choose your language (or "auto" for detection)
   - **Model**: Select model size (base recommended for balance)
   - **Overlay**: Configure overlay position and appearance

### Using VocalNode

**Toggle Mode (Default)**
1. Press your configured hotkey (e.g., F8) to start recording
2. Speak into your microphone
3. Press the hotkey again to stop and transcribe

**Hold Mode**
1. Hold your configured hotkey to record
2. Speak while holding the key
3. Release the key to stop and transcribe

**Visual Feedback**
- A floating overlay shows when you're listening
- The overlay displays transcribed text preview
- Tray icon changes color based on state:
  - Blue = Idle/Ready
  - Green = Listening/Recording

**Text Insertion**: The transcribed text will automatically be typed into the active window where your cursor is located.

### Stopping the Application

- Right-click the tray icon → "Quit"
- Or from terminal: `pkill -f "python.*run.py"`

## Configuration

Configuration is stored in `~/.vocalnode/config.json`. You can edit this file directly or use the Settings window.

### Hotkey Modes

- **Toggle**: Press once to start recording, press again to stop
- **Hold**: Hold the key while speaking, release to stop recording

### Models

- **tiny**: Fastest, least accurate (~39MB)
- **base**: Balanced speed/accuracy (~150MB) - **Recommended**
- **small**: Better accuracy (~500MB)
- **medium**: High accuracy (~1.5GB)
- **large**: Best accuracy (~3GB)

### Languages

Supports 99+ languages. Set to "auto" for automatic language detection.

## Troubleshooting

### Audio Device Not Found

- Check that your microphone is connected and recognized by your system
- Use the Settings window to refresh and select your audio device
- On Linux, ensure you have proper audio permissions

### Hotkey Not Working

- On Linux, you may need to run with appropriate permissions
- On macOS, grant accessibility permissions in System Preferences
- Try a different key combination

### Model Download Issues

- Models are downloaded automatically on first use
- Check your internet connection for initial download
- Models are cached in `~/.vocalnode/models/`

### Text Not Inserting

- Ensure the target application accepts text input
- Some applications may block simulated keyboard input
- Try switching to clipboard paste method in settings

## Platform-Specific Notes

### Linux

- Works with X11 and Wayland
- May require audio system configuration (ALSA/PulseAudio)
- Global hotkeys work best with X11

### Windows

- Requires Windows 10 or later
- May need to run as administrator for global hotkeys in some cases

### macOS

- Requires macOS 10.14 or later
- Grant accessibility permissions for text insertion
- Grant microphone permissions when prompted

## Development

### Project Structure

```
VocalNode/
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── tray_icon.py         # System tray icon
│   ├── settings_window.py   # Settings GUI
│   ├── hotkey_manager.py    # Global hotkey handling
│   ├── audio_capture.py     # Audio input
│   ├── stt_engine.py        # Speech-to-text engine
│   ├── dictation_overlay.py # Visual feedback overlay
│   └── text_inserter.py     # Text insertion
├── requirements.txt
└── README.md
```

## License

MIT License

## Credits

- Uses [faster-whisper](https://github.com/guillaumekln/faster-whisper) for speech-to-text
- Built with PyQt6 for cross-platform GUI


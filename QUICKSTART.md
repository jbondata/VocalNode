# Quick Start Guide

## Installation Complete! ✅

All dependencies have been successfully installed.

## Running VocalNode

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run the application:**
   ```bash
   python3 run.py
   ```

   Or:
   ```bash
   python3 -m src.main
   ```

## First Time Setup

1. **The app will appear in your system tray** (look for the microphone icon)

2. **On first run**, the Whisper model will be downloaded automatically (~150MB for base model)
   - This happens in the background
   - You'll see a notification when it's ready

3. **Configure settings:**
   - Right-click the tray icon
   - Select "Settings"
   - Configure:
     - **Hotkey**: Choose your preferred key (default: F8)
     - **Mode**: Toggle (press to start/stop) or Hold (hold to record)
     - **Audio Device**: Select your microphone
     - **Language**: Choose your language (or "auto" for detection)
     - **Model**: base (recommended) or other sizes

## Using VocalNode

### Toggle Mode (Default)
1. Press your configured hotkey (e.g., F8) to start recording
2. Speak into your microphone
3. Press the hotkey again to stop and transcribe

### Hold Mode
1. Hold your configured hotkey to record
2. Speak while holding
3. Release the key to stop and transcribe

### Visual Feedback
- A floating overlay shows when you're listening
- The overlay displays transcribed text preview
- Tray icon changes color based on state (blue=idle, green=listening)

## Troubleshooting

### Application won't start
- Make sure virtual environment is activated: `source venv/bin/activate`
- Check system tray is available (required for the app)

### Hotkey not working
- On Linux: May need X11 (Wayland support varies)
- On macOS: Grant Accessibility permissions
- On Windows: May need to run as Administrator

### Audio not working
- Check microphone permissions
- Verify audio device in Settings
- On Linux: May need `portaudio` system package

### Model download issues
- Check internet connection (needed for first download)
- Models are cached in `~/.vocalnode/models/`

## Stopping the Application

- Right-click tray icon → "Quit"
- Or use Ctrl+C in terminal

## Need Help?

Check the full README.md for more details and troubleshooting.



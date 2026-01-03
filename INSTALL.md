# Installation Guide

## Prerequisites

- Python 3.10 or higher (you have Python 3.13.11 ✓)
- pip (Python package manager)

## Install pip (if not already installed)

### On Arch Linux:
```bash
sudo pacman -S python-pip
```

### On Ubuntu/Debian:
```bash
sudo apt-get install python3-pip
```

### On macOS:
```bash
# Usually comes with Python, or use:
brew install python3
```

### On Windows:
```bash
# Usually comes with Python, or download from python.org
```

## Install Dependencies

Once pip is installed, run:

```bash
pip install -r requirements.txt
```

Or if you need to use pip3:

```bash
pip3 install -r requirements.txt
```

Or if you're using a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Application

After installing dependencies:

```bash
python3 run.py
```

Or:

```bash
python3 -m src.main
```

## First Run

1. The application will appear in your system tray
2. On first run, it will download the Whisper model (base model, ~150MB)
3. Right-click the tray icon and select "Settings" to configure:
   - Your preferred hotkey (default: F8)
   - Toggle or Hold mode
   - Microphone device
   - Language
   - Model size

## Troubleshooting

### Permission Issues (Linux)
- You may need to grant microphone permissions
- For global hotkeys, you might need to run with appropriate permissions

### macOS Specific
- Grant Accessibility permissions in System Preferences > Security & Privacy
- Grant Microphone permissions when prompted

### Windows Specific
- Run as Administrator if hotkeys don't work
- Grant microphone permissions in Windows Settings



#!/bin/bash
# Check if dependencies are installed

echo "Checking VocalNode installation..."
echo ""

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

echo "Checking installed packages:"
echo ""

packages=("faster-whisper" "PyQt6" "pynput" "sounddevice" "numpy" "pyyaml" "pyperclip")
all_installed=true

for pkg in "${packages[@]}"; do
    if pip show "$pkg" > /dev/null 2>&1; then
        version=$(pip show "$pkg" | grep Version | awk '{print $2}')
        echo "✅ $pkg: $version"
    else
        echo "❌ $pkg: NOT INSTALLED"
        all_installed=false
    fi
done

echo ""

if [ "$all_installed" = true ]; then
    echo "✅ All dependencies installed!"
    echo ""
    echo "To run VocalNode:"
    echo "  source venv/bin/activate"
    echo "  python3 run.py"
else
    echo "❌ Some dependencies are missing."
    echo "Run: venv/bin/pip install -r requirements.txt"
fi


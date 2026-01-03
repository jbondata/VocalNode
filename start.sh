#!/bin/bash
# Launcher script for VocalNode

cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Run: python3 -m venv venv"
    exit 1
fi

# Run the application
python3 run.py "$@"



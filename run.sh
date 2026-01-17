#!/bin/bash

# Default mode is 'news' if no argument is provided
MODE=${1:-news}

# Force le script à se déplacer dans son propre dossier
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    # Activate existing virtual environment
    source venv/bin/activate
fi

# Run the main script with mode argument
echo "Starting application in '$MODE' mode..."
python3 main.py "$MODE"

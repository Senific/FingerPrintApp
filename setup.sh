#!/bin/bash

set -e

# --- Configuration ---
PROJECT_DIR="/home/admin/FingerPrintApp"
VENV_PATH="/home/admin/senific_env"
PYTHON_BIN="/usr/bin/python3"

echo "🔧 Step 1: Creating virtual environment outside project..."
if [ -d "$VENV_PATH" ]; then
    echo "⚠️ Virtual environment already exists at $VENV_PATH"
else
    $PYTHON_BIN -m venv "$VENV_PATH"
    echo "✅ Virtual environment created at $VENV_PATH"
fi

echo "🔧 Step 2: Activating environment and installing requirements..."
source "$VENV_PATH/bin/activate"

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR/requirements.txt"
    echo "✅ Requirements installed from $PROJECT_DIR/requirements.txt"
else
    echo "❌ No requirements.txt found at $PROJECT_DIR"
    exit 1
fi

deactivate

# Add user to gpio group:
sudo usermod -aG gpio admin

#This is to Enable FingerPrint touch sensor 
sudo apt update
sudo apt install python3-gpiozero


echo "🎉 Environment setup complete!"



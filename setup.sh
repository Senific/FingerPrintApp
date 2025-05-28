#!/bin/bash
set -e

# === CONFIG ===
APP_DIR="FingerPrintApp"
VENV_DIR="$HOME/kivy_venv"
PYTHON_BIN="$VENV_DIR/bin/python3"
PIP_BIN="$VENV_DIR/bin/pip"

# === STEP 1: Create virtual environment ===
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# === STEP 2: Activate and install dependencies ===
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing dependencies..."
$PIP_BIN install --upgrade pip setuptools wheel Cython
$PIP_BIN install kivy[base] kivy[full]

# === STEP 3: Run the app ===
echo "Running the Kivy app..."
cd "$APP_DIR"
$PYTHON_BIN main.py

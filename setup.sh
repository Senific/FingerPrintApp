#!/bin/bash
set -e

# === CONFIG ===
APP_DIR="FingerPrintApp"
VENV_DIR="$HOME/my_venv"
PYTHON_BIN="$VENV_DIR/bin/python3"
PIP_BIN="$VENV_DIR/bin/pip"

echo "=========================="
echo "Installing system packages"
echo "=========================="
sudo apt update
sudo apt install -y \
  python3 python3-venv python3-pip git \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
  zlib1g-dev libgstreamer1.0-dev gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
  gstreamer1.0-libav gstreamer1.0-alsa libmtdev-dev \
  libgl1-mesa-dev libgles2-mesa-dev xclip xsel libjpeg-dev

sudo apt update
sudo apt-get install -y \
  libavcodec-dev \
  libavdevice-dev \
  libavfilter-dev \
  libavformat-dev \
  libavutil-dev \
  libswscale-dev \
  libswresample-dev \
  libpostproc-dev \
  libsdl2-dev


# === STEP 1: Create virtual environment ===
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# === STEP 2: Activate and install Python dependencies ===
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing dependencies..."
$PIP_BIN install --upgrade pip setuptools wheel Cython

# Use kivy[full] if you need audio/video support, or kivy[base] if not
echo "Installing Kivy and dependencies..."
$PIP_BIN install kivy

# === STEP 3: Run the app ===
echo "Running the Kivy app..."
cd ..
cd "$APP_DIR"
$PYTHON_BIN main.py

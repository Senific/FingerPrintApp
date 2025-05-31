#!/bin/bash

set -e

APP_DIR="/home/admin/FingerPrintApp"
VENV_DIR="/home/admin/senific_venv"
PYTHON_BIN="/usr/bin/python3"

echo "🔧 Step 1: Creating Python virtual environment at $VENV_DIR..."
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON_BIN -m venv "$VENV_DIR"
fi

echo "📦 Step 2: Activating virtual environment and installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install kivy

echo "🖥️ Step 3: Installing ILI9486 LCD driver..."

# Install required packages
sudo apt-get update
sudo apt-get install -y cmake dkms git raspberrypi-kernel-headers

# Clone LCD driver repo outside app directory
LCD_DRIVER_DIR="/home/admin/ili9486_driver"
if [ ! -d "$LCD_DRIVER_DIR" ]; then
    git clone https://github.com/Elecrow-keen/Elecrow-LCD35.git "$LCD_DRIVER_DIR"
fi

cd "$LCD_DRIVER_DIR"
sudo bash ./LCD35-show

echo "✅ LCD driver installed — Raspberry Pi will reboot to apply changes."
echo "🌀 Rebooting in 5 seconds... Press Ctrl+C to cancel."
sleep 5
sudo reboot

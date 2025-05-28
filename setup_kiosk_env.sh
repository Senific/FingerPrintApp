#!/bin/bash
set -e

echo "📦 Updating and installing packages..."
sudo apt update && sudo apt upgrade -y

sudo apt install -y cmake git python3-pip python3-dev python3-venv \
  libgl1-mesa-dev libgles2-mesa-dev libgstreamer1.0-dev \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  libmtdev-dev libinput-dev libjpeg-dev libpng-dev libfreetype6-dev \
  libffi-dev libssl-dev libportmidi-dev libavformat-dev \
  libswscale-dev libavcodec-dev zlib1g-dev

echo "🖥️ Cloning and building fbcp-ili9341 with ILI9486 support..."
cd ~
git clone https://github.com/juj/fbcp-ili9341.git
cd fbcp-ili9341
mkdir -p build && cd build
cmake -DILI9486=ON -DSPI_BUS_CLOCK_DIVISOR=6 -DDISPLAY_ROTATE_180_DEGREES=ON ..
make -j

echo "🐍 Setting up Kivy virtual environment..."
cd ~
python3 -m venv kivy_venv
source kivy_venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install "kivy[base]"

echo "✅ Environment setup complete."

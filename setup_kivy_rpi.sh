#!/bin/bash

# Exit immediately on error
set -e

echo "Updating system..."
sudo apt update && sudo apt full-upgrade -y

echo "Installing system dependencies..."
sudo apt install -y \
  python3-pip \
  python3-venv \
  git \
  libsdl2-dev \
  libsdl2-image-dev \
  libsdl2-mixer-dev \
  libsdl2-ttf-dev \
  libportmidi-dev \
  libswscale-dev \
  libavformat-dev \
  libavcodec-dev \
  zlib1g-dev \
  libgstreamer1.0 \
  libgstreamer1.0-dev \
  libmtdev-dev \
  xclip \
  libjpeg-dev \
  libfreetype6-dev \
  libgl1-mesa-dev \
  libgles2-mesa-dev \
  libgpiod-dev \
  libinput-dev \
  libudev-dev \
  libasound2-dev \
  libdrm-dev \
  libgbm-dev \
  ffmpeg \
  pkg-config \
  build-essential \
  libx11-dev \
  mesa-utils \
  libegl1-mesa-dev \
  libsdl2-ttf-2.0-0 \
  libwayland-dev \
  libdecor-0-dev

echo "Creating virtual environment..."
python3 -m venv ~/kivy_venv
source ~/kivy_venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel Cython

echo "Installing Kivy..."
pip install kivy[base] kivy[full]

echo "All done."
echo "To run your Kivy app:"
echo "1. Activate the virtual environment: source ~/kivy_venv/bin/activate"
echo "2. Run your app with: python3 main.py"

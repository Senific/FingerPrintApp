#!/bin/bash
set -e

echo "Updating system..."
sudo apt update && sudo apt full-upgrade -y

echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

echo "Installing dependencies for LCD driver..."
sudo apt install -y git bc raspberrypi-kernel-headers build-essential device-tree-compiler

echo "Cloning LCD driver repo..."
cd ~
if [ ! -d "LCD-show" ]; then
    git clone https://github.com/waveshare/LCD-show.git
fi

echo "Running LCD driver installation script..."
cd LCD-show
sudo ./LCD35-show  # Adjust this if your screen uses a different script

echo "Rebooting system to apply changes..."
sudo reboot
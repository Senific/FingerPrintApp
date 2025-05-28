#!/bin/bash
set -e

echo "📦 Installing dependencies..."
sudo apt update
sudo apt install -y raspberrypi-kernel-headers git build-essential dkms device-tree-compiler

echo "🖥️ Cloning LCD driver repo..."
cd /home/Admin
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show

echo "🛠️ Installing 3.5-inch ILI9486 driver..."
# This script will:
# - Copy kernel module
# - Modify config.txt
# - Enable SPI
# - Set display rotation

sudo chmod +x LCD35-show
sudo ./LCD35-show

# It will auto-reboot. If not, prompt user:
echo "✅ Driver install script complete. If not rebooted automatically, please run:"
echo "   sudo reboot"

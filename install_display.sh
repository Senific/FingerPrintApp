#!/bin/bash

set -e

echo "=== Updating system ==="
sudo apt update && sudo apt full-upgrade -y

echo "=== Enabling SPI interface ==="
sudo raspi-config nonint do_spi 0

echo "=== Installing required packages ==="
sudo apt install -y git fbi

echo "=== Cloning LCD driver repository to home directory ==="
cd /home/Admin
if [ -d "/home/Admin/LCD-show" ]; then
    echo "LCD-show already exists, removing..."
    rm -rf "/home/Admin/LCD-show"
fi

git clone https://github.com/goodtft/LCD-show.git /home/Admin/LCD-show
cd /home/Admin/LCD-show
chmod +x LCD35-show

echo "=== Installing ILI9486 driver (will reboot) ==="
sudo ./LCD35-show

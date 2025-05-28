#!/bin/bash

set -e

echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo "Installing required dependencies..."
sudo apt-get install -y git bc

cd ..

echo "Cloning ILI9486 driver repository..."
if [ ! -d "LCD-show" ]; then
    git clone https://github.com/goodtft/LCD-show.git
else
    echo "LCD-show repo already exists, pulling latest changes..."
    cd LCD-show
    git pull
    cd ..
fi

echo "Running ILI9486 LCD driver install script..."
cd LCD-show/
# There are usually scripts like LCD35-show.sh or similar
# Assuming your LCD uses 3.5-inch ILI9486 driver:
sudo ./LCD35-show.sh

echo "Driver installation complete. Rebooting in 5 seconds..."
sleep 5
sudo reboot

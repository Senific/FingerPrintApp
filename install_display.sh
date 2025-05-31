#!/bin/bash

set -e

echo "🔧 Installing ILI9486 driver for 3.5\" LCD..."

# Store current directory (your project repo)
PROJECT_DIR=$(pwd)

# Use a safe temp location outside the project
WORK_DIR="$HOME/ILI9486_DriverInstall"

# Step 1: Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install required packages
echo "📦 Installing dependencies..."
sudo apt install -y git raspberrypi-kernel-headers build-essential dkms device-tree-compiler

# Step 3: Clone the driver repo outside the project directory
echo "📁 Cloning LCD-show repo to $WORK_DIR..."
rm -rf "$WORK_DIR"
git clone https://github.com/goodtft/LCD-show.git "$WORK_DIR"

# Step 4: Run the install script
cd "$WORK_DIR"
chmod +x LCD35-show

echo "⚙️ Installing LCD35 (ILI9486) driver..."
sudo ./LCD35-show

# NOTE: This will reboot the Pi automatically if successful

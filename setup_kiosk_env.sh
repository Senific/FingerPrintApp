#!/bin/bash

set -e

# Update and install dependencies
sudo apt-get update
sudo apt-get install -y cmake git build-essential libboost-dev libudev-dev

# Clone fbcp-ili9341
cd ~
if [ ! -d fbcp-ili9341 ]; then
    git clone https://github.com/juj/fbcp-ili9341.git
fi

# Build it natively (no cross-compile flags)
cd ~/fbcp-ili9341
mkdir -p build
cd build
cmake -DWAVESHARE_ILI9341=ON ..
make -j$(nproc)

# Optional: Enable SPI and configure to run on boot
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
fi

# Autostart fbcp-ili9341 on boot (optional)
SERVICE_FILE="/etc/systemd/system/fbcp-ili9341.service"
if [ ! -f "$SERVICE_FILE" ]; then
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Framebuffer copy for ILI9341
After=network.target

[Service]
ExecStart=/home/Admin/fbcp-ili9341/build/fbcp-ili9341
Restart=always
User=Admin

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl enable fbcp-ili9341
    sudo systemctl start fbcp-ili9341
fi

echo "fbcp-ili9341 installed and configured."

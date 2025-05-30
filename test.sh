#!/bin/bash
set -e

APP_USER="admin"
APP_DIR="/home/$APP_USER/FingerPrintApp"
PYTHON_BIN="/usr/bin/python3"
SERVICE_FILE="/etc/systemd/system/fingerprint-kiosk.service"

echo "📦 Installing 3.5\" LCD driver (GoodTFT)..."
if [ ! -d "LCD-show" ]; then
  git clone https://github.com/goodtft/LCD-show.git
fi
cd LCD-show
sudo chmod +x LCD35-show
sudo ./LCD35-show

echo "📁 Setting up systemd service for Kivy App..."

cat <<EOF | sudo tee "$SERVICE_FILE" > /dev/null
[Unit]
Description=Kivy Fingerprint App on 3.5in LCD
After=multi-user.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=/bin/bash -c 'export SDL_FBDEV=/dev/fb1; export KIVY_WINDOW=egl_rpi; $PYTHON_BIN main.py'
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo "✅ Enabling fingerprint kiosk service..."
sudo systemctl enable fingerprint-kiosk.service

echo "📌 Done. Your Kivy app will launch automatically on the 3.5\" LCD after reboot."
echo "🌀 Rebooting now..."
sudo reboot

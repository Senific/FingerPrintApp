#!/bin/bash

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$HOME/fingerprint-env"
PYTHON="$ENV_DIR/bin/python"
SERVICE_NAME="kiosk.service"

echo "🔧 Installing system dependencies..."
sudo apt update
sudo apt install -y git python3-full python3-venv python3-pip

echo "🐍 Creating virtual environment at $ENV_DIR..."
python3 -m venv "$ENV_DIR"

echo "📦 Installing Python dependencies..."
source "$ENV_DIR/bin/activate"
pip install --upgrade pip
pip install kivy




echo "🛠️ Setting up systemd service..."

SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Kivy App Kiosk
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON $APP_DIR/main.py
Restart=always
User=$USER
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "🔁 Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Setup complete! Use 'sudo systemctl status $SERVICE_NAME' to check status."

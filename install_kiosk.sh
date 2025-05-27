#!/bin/bash

APP_PATH="$(dirname $(realpath $0))/../main.py"
VENV_PATH="$(dirname $(realpath $0))/../fingerprint-env/bin/python"

SERVICE_PATH="/etc/systemd/system/kiosk.service"

echo "Creating kiosk systemd service..."

sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Kivy App Kiosk
After=network.target

[Service]
ExecStart=$VENV_PATH $APP_PATH
WorkingDirectory=$(dirname $APP_PATH)
Restart=always
User=$USER
Environment=PYTHONUNBUFFERED=1
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl restart kiosk.service

echo "Kiosk service installed and started."

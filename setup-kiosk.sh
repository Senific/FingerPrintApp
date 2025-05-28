#!/bin/bash

# KIOSK CONFIGURATION SCRIPT

APP_DIR="/home/Admin/FingerPrintApp"
VENV_DIR="/home/Admin/fingerprint-env"
SERVICE_NAME="kiosk"
USER_NAME="Admin"

echo "Creating systemd service for kiosk..."

# Create systemd service
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Kiosk Fingerprint App
After=multi-user.target
Wants=graphical.target

[Service]
Type=simple
User=${USER_NAME}
WorkingDirectory=${APP_DIR}
Environment=DISPLAY=
Environment=PYTHONUNBUFFERED=1
Environment=KIVY_METRICS_DENSITY=1
Environment=KIVY_WINDOW=sdl2
Environment=KIVY_GL_BACKEND=gl
Environment=SDL_VIDEODRIVER=fbcon
Environment=SDL_FBDEV=/dev/fb1
ExecStart=${VENV_DIR}/bin/python3 ${APP_DIR}/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service
sudo systemctl start ${SERVICE_NAME}.service

echo "Kiosk service '${SERVICE_NAME}' has been installed and started."
echo "Run 'sudo journalctl -u ${SERVICE_NAME} -f' to view live logs."

#!/bin/bash

# Configuration
APP_DIR="/home/admin/FingerPrintApp"
VENV_DIR="$APP_DIR/my_venv"
PYTHON_EXEC="$VENV_DIR/bin/python"
APP_ENTRY="main.py"
SERVICE_NAME="fingerprintapp"

# Ensure script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root. Use: sudo ./setup_kiosk_app.sh"
   exit 1
fi

# Ensure ILI9486 LCD is configured
echo "✅ Configuring ILI9486 LCD for console..."
if ! grep -q "fbcon=map:1" /boot/cmdline.txt; then
  sed -i 's/$/ fbcon=map:1 fbcon=font:VGA8x8/' /boot/cmdline.txt
fi

# Enable SPI for ILI9486 (if not already)
raspi-config nonint do_spi 0

# Create systemd service file
echo "✅ Creating systemd service for FingerPrintApp..."
cat <<EOF > /etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=FingerPrintApp Kivy Kiosk Service
After=network.target

[Service]
User=admin
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON_EXEC $APP_DIR/$APP_ENTRY
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Permissions
chmod 644 /etc/systemd/system/${SERVICE_NAME}.service

# Enable and start the service
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}.service
systemctl start ${SERVICE_NAME}.service

echo "✅ FingerPrintApp service installed and running."
echo "🔁 The app will now run on boot, restart on crash, and block other GUI."

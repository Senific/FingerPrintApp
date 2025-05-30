#!/bin/bash

set -e

USERNAME="admin"
APP_DIR="/home/$USERNAME/FingerPrintApp"
VENV_DIR="/home/$USERNAME/my_venv"
SERVICE_NAME="fingerprint-kiosk"

echo "🔧 Disabling boot messages and splash..."

# Update /boot/config.txt
CONFIG="/boot/config.txt"
grep -qxF "disable_splash=1" $CONFIG || echo "disable_splash=1" >> $CONFIG
grep -qxF "framebuffer_width=480" $CONFIG || echo "framebuffer_width=480" >> $CONFIG
grep -qxF "framebuffer_height=320" $CONFIG || echo "framebuffer_height=320" >> $CONFIG

# Update /boot/cmdline.txt
CMDLINE="/boot/cmdline.txt"
CMDLINE_TEXT="console=tty3 loglevel=0 quiet splash plymouth.enable=0 fbcon=map:10 fbcon=font:VGA8x8"
echo $CMDLINE_TEXT | sudo tee $CMDLINE > /dev/null

echo "✅ Boot messages suppressed."

echo "🔒 Enabling autologin to console..."
sudo raspi-config nonint do_boot_behaviour B2

echo "✅ Console autologin set."

echo "🛠️ Creating systemd service for Kivy app..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
cat <<EOF | sudo tee $SERVICE_FILE > /dev/null
[Unit]
Description=FingerprintApp Kiosk
After=multi-user.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python main.py
Environment=KIVY_BCM_DISPMANX_ID=2
Environment=DISPLAY=:0
StandardOutput=journal
StandardError=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo "🔁 Enabling and starting the service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME.service

echo "✅ Kiosk service installed. Your app will launch on boot."

echo "🚀 All done! Rebooting in 5 seconds..."
sleep 5
sudo reboot

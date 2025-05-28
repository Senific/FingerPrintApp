#!/bin/bash

# Variables - adjust if needed
APP_DIR="/home/Admin/FingerPrintApp"
LAUNCHER="/root/start_fingerprint.sh"
SERVICE_FILE="/etc/systemd/system/fingerprintapp.service"
LOG_FILE="/var/log/fingerprintapp.log"
FB_DEVICE="/dev/fb1"

echo "Creating launcher script at $LAUNCHER..."

cat << EOF > $LAUNCHER
#!/bin/bash
export KIVY_WINDOW=sdl2
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=$FB_DEVICE
export SDL_NOMOUSE=1

cd $APP_DIR
python3 main.py >> $LOG_FILE 2>&1
EOF

chmod +x $LAUNCHER
echo "Launcher script created and made executable."

echo "Creating systemd service file at $SERVICE_FILE..."

cat << EOF > $SERVICE_FILE
[Unit]
Description=Fingerprint Kivy App Kiosk
After=network.target

[Service]
Type=simple
User=root
ExecStart=$LAUNCHER
Restart=always
RestartSec=5

StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=fingerprintapp

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon and enabling service..."
systemctl daemon-reload
systemctl enable fingerprintapp.service
systemctl start fingerprintapp.service

echo "Setup complete. Your app should now run on boot as root using framebuffer."
echo "Check logs with: journalctl -u fingerprintapp -f"

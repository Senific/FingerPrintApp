#!/bin/bash
set -e

USER="admin"
HOME_DIR="/home/$USER"
APP_DIR="$HOME_DIR/FingerPrintApp"
VENV_DIR="$HOME_DIR/my_venv"
PYTHON="$VENV_DIR/bin/python"
MAIN_SCRIPT="$APP_DIR/main.py"
LOG_FILE="$HOME_DIR/fingerprintapp.log"
SERVICE_FILE="/etc/systemd/system/kivyapp.service"

echo "----------------------------------------"
echo "1. Re-enable TTY1 (if masked)"
echo "----------------------------------------"
sudo systemctl unmask getty@tty1.service
sudo systemctl enable getty@tty1.service

echo "----------------------------------------"
echo "2. Install Plymouth and configure splash"
echo "----------------------------------------"

sudo apt-get update
sudo apt-get install -y plymouth plymouth-theme-pix

echo "Setting Plymouth theme to pix..."
sudo plymouth-set-default-theme -R pix

# Backup cmdline.txt before modifying
if [ ! -f /boot/cmdline.txt.bak ]; then
    sudo cp /boot/cmdline.txt /boot/cmdline.txt.bak
fi

# Clean existing quiet, splash, loglevel entries
sudo sed -i 's/\bquiet\b//g' /boot/cmdline.txt
sudo sed -i 's/\bsplash\b//g' /boot/cmdline.txt
sudo sed -i 's/\bloglevel=[0-9]\b//g' /boot/cmdline.txt
sudo sed -i 's/\bvt.global_cursor_default=[01]\b//g' /boot/cmdline.txt

# Append parameters, keep single line
sudo sed -i '1s/$/ quiet splash loglevel=3 vt.global_cursor_default=0/' /boot/cmdline.txt

echo "----------------------------------------"
echo "3. Create systemd service to start Kivy app"
echo "----------------------------------------"

sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Start Kivy App with X Server
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=DISPLAY=:0
ExecStart=/bin/bash -c '
  while true; do
    echo \"Starting Kivy app...\" >> \"$LOG_FILE\"
    date >> \"$LOG_FILE\"
    startx /usr/bin/python3 $MAIN_SCRIPT >> \"$LOG_FILE\" 2>&1
    echo \"App exited. Restarting in 3 seconds...\" >> \"$LOG_FILE\"
    sleep 3
  done
'
Restart=always
RestartSec=5
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable kivyapp.service

echo "----------------------------------------"
echo "4. Ensure log file exists and has proper ownership"
echo "----------------------------------------"

sudo touch "$LOG_FILE"
sudo chown $USER:$USER "$LOG_FILE"

echo "✅ Setup complete. Please reboot to see Plymouth splash and auto-start your Kivy app."

# Optional immediate reboot
# echo "Rebooting now..."
# sleep 5
# sudo reboot

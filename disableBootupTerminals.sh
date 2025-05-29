#!/bin/bash
set -e

# --- Configuration ---
USER="admin"
HOME_DIR="/home/$USER"
APP_DIR="$HOME_DIR/FingerPrintApp"
VENV_DIR="$HOME_DIR/my_venv"
LAUNCH_SCRIPT="$HOME_DIR/start-kivy.sh"
SERVICE_FILE="/etc/systemd/system/kivyapp.service"
LOG_FILE="$HOME_DIR/fingerprintapp.log"

echo "----------------------------------------"
echo "1. Disabling all TTYs..."
echo "----------------------------------------"
for i in {1..6}; do
  sudo systemctl mask getty@tty$i.service
done

echo "----------------------------------------"
echo "2. Hiding Boot Logs and Rainbow Splash..."
echo "----------------------------------------"

# Hide boot messages, enable quiet splash
sudo sed -i 's/console=tty1/console=tty3/' /boot/cmdline.txt
sudo sed -i 's/$/ quiet splash loglevel=0 vt.global_cursor_default=0/' /boot/cmdline.txt

# Disable rainbow splash
if ! grep -q "disable_splash=1" /boot/config.txt; then
  echo "disable_splash=1" | sudo tee -a /boot/config.txt
fi

# Disable blinking cursor
sudo bash -c 'echo "setterm -cursor off" >> /etc/rc.local'

echo "----------------------------------------"
echo "3. Creating launch script for Kivy app..."
echo "----------------------------------------"
sudo -u $USER bash << EOF
cat > "$LAUNCH_SCRIPT" << 'EOAPP'
#!/bin/bash
export DISPLAY=:0
export XAUTHORITY=/home/$USER/.Xauthority

# Start X if not running
if ! pgrep Xorg; then
  startx &
  sleep 5
fi

xset -dpms
xset s off
xset s noblank

while true; do
    echo "Starting Kivy app..." >> "$LOG_FILE"
    date >> "$LOG_FILE"
    cd "$APP_DIR" || exit 1
    source "$VENV_DIR/bin/activate"
    "$VENV_DIR/bin/python" main.py >> "$LOG_FILE" 2>&1
    echo "App crashed or exited. Restarting in 3 seconds..." >> "$LOG_FILE"
    sleep 3
done
EOAPP

chmod +x "$LAUNCH_SCRIPT"
EOF

echo "----------------------------------------"
echo "4. Creating systemd service..."
echo "----------------------------------------"
sudo bash -c "cat > $SERVICE_FILE" << EOSERVICE
[Unit]
Description=Kivy App Auto Boot
After=multi-user.target graphical.target

[Service]
User=$USER
WorkingDirectory=$HOME_DIR
ExecStart=$LAUNCH_SCRIPT
Restart=always
Environment=DISPLAY=:0
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOSERVICE

echo "----------------------------------------"
echo "5. Enabling and starting the service..."
echo "----------------------------------------"
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable kivyapp.service

echo "----------------------------------------"
echo "✅ Setup complete. Rebooting into your app..."
echo "----------------------------------------"
sleep 3
sudo reboot

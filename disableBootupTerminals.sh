#!/bin/bash
set -e

USER="admin"
HOME_DIR="/home/$USER"
APP_DIR="$HOME_DIR/FingerPrintApp"
VENV_DIR="$HOME_DIR/my_venv"
PYTHON="$VENV_DIR/bin/python"
MAIN_SCRIPT="$APP_DIR/main.py"
LOG_FILE="$HOME_DIR/fingerprintapp.log"
XINITRC="$HOME_DIR/.xinitrc"

echo "----------------------------------------"
echo "1. Disable Getty on TTY1"
echo "----------------------------------------"
sudo systemctl disable getty@tty1.service || true

echo "----------------------------------------"
echo "2. Create .xinitrc to Launch Kivy App"
echo "----------------------------------------"
sudo -u "$USER" bash << 'EOF'
cat > "$HOME/.xinitrc" << EOX
#!/bin/bash
xset -dpms
xset s off
xset s noblank
while true; do
  echo "Starting Kivy app..." >> "$HOME/fingerprintapp.log"
  date >> "$HOME/fingerprintapp.log"
  cd "$HOME/FingerPrintApp"
  source "$HOME/my_venv/bin/activate"
  "$HOME/my_venv/bin/python" main.py >> "$HOME/fingerprintapp.log" 2>&1
  echo "App crashed or exited. Restarting in 3 seconds..." >> "$HOME/fingerprintapp.log"
  sleep 3
done
EOX

chmod +x "$HOME/.xinitrc"
EOF

echo "----------------------------------------"
echo "3. Create Systemd Service to Run X on Boot"
echo "----------------------------------------"
SERVICE_FILE="/etc/systemd/system/kivy-app.service"
sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Start Kivy App with X
After=multi-user.target

[Service]
User=$USER
Environment=DISPLAY=:0
Environment=XAUTHORITY=$HOME_DIR/.Xauthority
ExecStart=/usr/bin/startx
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable kivy-app.service

echo "----------------------------------------"
echo "4. Clean Up Getty & Set Permissions"
echo "----------------------------------------"
sudo systemctl disable getty@tty1.service || true
sudo chown "$USER:$USER" "$XINITRC"
sudo chown "$USER:$USER" "$LOG_FILE"

echo "----------------------------------------"
echo "5. Show All Created Files"
echo "----------------------------------------"
echo "Created files:"
echo "$XINITRC"
echo "$SERVICE_FILE"
echo "$LOG_FILE"

echo "----------------------------------------"
echo "✅ Setup complete. Rebooting now to boot into your app..."
echo "----------------------------------------"
sleep 5
sudo reboot

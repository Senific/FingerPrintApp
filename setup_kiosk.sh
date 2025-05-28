#!/bin/bash

# Constants
APP_PATH="/home/Admin/FingerPrintApp/main.py"
START_SCRIPT="/home/Admin/start_kiosk.sh"
XINITRC="/home/Admin/.xinitrc"
SERVICE_FILE="/etc/systemd/system/kiosk.service"

# Check correct user
if [ "$USER" != "Admin" ]; then
  echo "❌ Run this as user: Admin"
  exit 1
fi

echo "🔄 Updating system..."
sudo apt update

echo "📦 Installing minimal X11 packages..."
sudo apt install -y xserver-xorg x11-xserver-utils xinit xterm

echo "📝 Creating start script outside the repo..."
cat <<EOF > "$START_SCRIPT"
#!/bin/bash
export DISPLAY=:0
export XAUTHORITY=/home/Admin/.Xauthority
python3 "$APP_PATH"
EOF

chmod +x "$START_SCRIPT"

echo "📝 Creating .xinitrc in Admin's home directory..."
cat <<EOF > "$XINITRC"
#!/bin/bash
exec $START_SCRIPT
EOF

chmod +x "$XINITRC"

echo "🛠️ Creating systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Kiosk Mode
After=network.target

[Service]
User=Admin
Environment=DISPLAY=:0
ExecStart=/usr/bin/xinit
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading and enabling kiosk.service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service

echo "✅ Kiosk setup complete. App will auto-start full-screen on boot."

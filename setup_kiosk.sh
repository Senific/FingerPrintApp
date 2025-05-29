#!/bin/bash

# === Config ===
APP_USER=$(whoami)
APP_HOME="/home/$APP_USER"
APP_DIR="$APP_HOME/FingerPrintApp"
APP_MAIN="$APP_DIR/main.py"
VENV_DIR="$APP_HOME/my_venv"
SERVICE_NAME="fingerprint-kiosk"
LOG_DIR="/tmp"
ENV_FILE="/etc/profile.d/kivy-fb.sh"

echo "🚀 Starting kiosk setup for $APP_USER"

# === 1. System Updates & Required Packages ===
echo "🔧 Installing required packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git libgl1-mesa-dev --no-install-recommends

# === 2. Setup Virtual Environment ===
echo "🐍 Creating virtual environment at $VENV_DIR..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip

if [ -f "$APP_DIR/requirements.txt" ]; then
  echo "📦 Installing dependencies from requirements.txt..."
  pip install -r "$APP_DIR/requirements.txt"
else
  echo "⚠️  requirements.txt not found. Please install manually if needed."
fi
deactivate

# === 3. Setup Framebuffer Environment Variables ===
echo "🧩 Setting SDL2 to use framebuffer /dev/fb1..."
sudo tee "$ENV_FILE" > /dev/null <<EOF
export KIVY_METRICS_DENSITY=1
export KIVY_BCM_DISPMANX_ID=1
export KIVY_WINDOW=sdl2
export SDL_FBDEV=/dev/fb1
export SDL_VIDEODRIVER=fbcon
export SDL_MOUSEDRV=TSLIB
export SDL_MOUSEDEV=/dev/input/event0
export KIVY_LOG_LEVEL=debug
EOF
sudo chmod +x "$ENV_FILE"

# === 4. Create systemd service ===
echo "🧠 Creating systemd service for app restart + boot..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Kivy Fingerprint App Kiosk (Framebuffer)
After=network.target

[Service]
User=$APP_USER
EnvironmentFile=$ENV_FILE
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python3 $APP_MAIN
Restart=always
RestartSec=2
StandardOutput=append:$LOG_DIR/${SERVICE_NAME}_stdout.log
StandardError=append:$LOG_DIR/${SERVICE_NAME}_stderr.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME.service

# === 5. Autologin to tty1 ===
echo "🔐 Enabling autologin to tty1..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $APP_USER --noclear %I \$TERM
EOF

# === 6. Disable other TTYs (optional) ===
echo "🚫 Disabling other TTYs..."
for tty in {2..6}; do
  sudo systemctl disable getty@tty$tty.service
done

# === 7. Silence console ===
echo "🔇 Silencing boot console messages..."
sudo sed -i 's/$/ quiet loglevel=0 console=tty3/' /boot/cmdline.txt 2>/dev/null || true

# === Done ===
echo "✅ Kiosk setup complete."
echo "📄 Logs: $LOG_DIR/${SERVICE_NAME}_stdout.log and stderr.log"
echo "🔁 Rebooting..."
sudo reboot

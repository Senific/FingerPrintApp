#!/bin/bash

# === CONFIGURATION ===
APP_USER=$(whoami)
APP_HOME="/home/$APP_USER"
APP_DIR="$APP_HOME/FingerPrintApp"
APP_MAIN="$APP_DIR/main.py"
VENV_DIR="$APP_HOME/my_venv"
SERVICE_NAME="fingerprint-kiosk"
LOG_DIR="/tmp"
XORG_CONF="/etc/X11/xorg.conf.d/99-fbdev.conf"

echo "🚀 Starting full kiosk setup for user: $APP_USER"

# === 1. Install Dependencies ===
echo "🔧 Installing system packages..."
sudo apt update
sudo apt install -y \
  python3 python3-pip python3-venv \
  git xserver-xorg x11-xserver-utils xinit xterm \
  libgl1-mesa-dev xserver-xorg-video-fbdev --no-install-recommends

# === 2. Create Python Virtual Environment ===
echo "🐍 Creating virtual environment at $VENV_DIR..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip

if [ -f "$APP_DIR/requirements.txt" ]; then
  echo "📦 Installing Python dependencies from requirements.txt..."
  pip install -r "$APP_DIR/requirements.txt"
else
  echo "⚠️  requirements.txt not found. Please install packages manually later."
fi
deactivate

# === 3. Configure X11 to use ILI9486 LCD (/dev/fb1) ===
echo "🖥️ Configuring X to use framebuffer /dev/fb1..."
sudo mkdir -p /etc/X11/xorg.conf.d
sudo tee "$XORG_CONF" > /dev/null <<EOF
Section "Device"
    Identifier  "FBDEV"
    Driver      "fbdev"
    Option      "fbdev" "/dev/fb1"
EndSection
EOF

# === 4. Create systemd Service ===
echo "🧠 Creating systemd service to launch your Kivy app..."

sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Kivy Fingerprint App Kiosk
After=multi-user.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=DISPLAY=:0
ExecStart=$VENV_DIR/bin/python3 $APP_MAIN
Restart=always
RestartSec=2
StandardOutput=append:$LOG_DIR/${SERVICE_NAME}_stdout.log
StandardError=append:$LOG_DIR/${SERVICE_NAME}_stderr.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME.service

# === 5. Enable Autologin on tty1 ===
echo "🔐 Enabling autologin on tty1 for $APP_USER..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $APP_USER --noclear %I \$TERM
EOF

# === 6. Clean Boot Settings (Silence Console) ===
echo "🧹 Silencing console output..."
sudo sed -i 's/$/ quiet loglevel=0 console=tty3/' /boot/cmdline.txt 2>/dev/null || true

# === 7. Disable Other TTYs ===
echo "🚫 Disabling extra TTY login prompts..."
for tty in {2..6}; do
  sudo systemctl disable getty@tty$tty.service
done

# === DONE ===
echo "✅ Kiosk setup complete."
echo "📄 Logs will appear in: $LOG_DIR/${SERVICE_NAME}_stdout.log and stderr.log"
echo "🔁 Rebooting to test systemd kiosk launch..."
sudo reboot

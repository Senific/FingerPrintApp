#!/bin/bash

APP_PATH="/home/Admin/FingerPrintApp/main.py"
APP_DIR="/home/Admin/FingerPrintApp"
VENV_DIR="/home/Admin/my_venv"
START_SCRIPT="/home/Admin/start_app.sh"
XINITRC="/home/Admin/.xinitrc"
SERVICE_FILE="/etc/systemd/system/kiosk.service"
USER="Admin"

# Check correct user
if [ "$USER" != "$(whoami)" ]; then
  echo "❌ Please run this script as user: $USER"
  exit 1
fi

echo "🔄 Updating system and installing required packages..."
sudo apt update
sudo apt install -y xserver-xorg x11-xserver-utils xinit xterm git python3 python3-venv python3-pip

echo "🧹 Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "📦 Installing Python dependencies in virtual environment..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
if [ -f "$APP_DIR/requirements.txt" ]; then
  pip install -r "$APP_DIR/requirements.txt"
fi
deactivate

echo "📝 Creating start_app.sh to launch app inside venv..."
cat <<EOF > "$START_SCRIPT"
#!/bin/bash
export DISPLAY=:0
source "$VENV_DIR/bin/activate"
python3 "$APP_PATH"
EOF
chmod +x "$START_SCRIPT"

echo "📝 Creating .xinitrc to launch start_app.sh..."
cat <<EOF > "$XINITRC"
#!/bin/bash
exec $START_SCRIPT
EOF
chmod +x "$XINITRC"

echo "🛠️ Creating kiosk.service systemd unit..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Kiosk Mode for $USER
After=network.target

[Service]
User=$USER
Environment=DISPLAY=:0
ExecStart=/usr/bin/xinit
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🔁 Reloading systemd daemon and enabling kiosk service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service

echo "🔐 Setting up autologin on tty1 for $USER..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d

sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $USER --noclear %I \$TERM
EOF

echo "🚫 Disabling getty login prompts on tty2-tty6..."
for tty in {2..6}; do
  sudo systemctl disable getty@tty$tty.service
done

echo "🧹 Adding quiet boot to /boot/cmdline.txt..."
if ! grep -q "quiet loglevel=0 console=tty3" /boot/cmdline.txt; then
  sudo sed -i 's/$/ quiet loglevel=0 console=tty3/' /boot/cmdline.txt
fi

echo "✅ Setup complete! Please reboot the system to start kiosk mode."

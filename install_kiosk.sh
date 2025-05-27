#!/bin/bash

set -e

echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip git python3-kivy libgl1 xinit

echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt || pip3 install kivy

echo "🛠️ Setting up X session to auto-start the app..."
cat <<EOF > ~/.xinitrc
#!/bin/bash
python3 ~/FingerPrintApp/main.py
EOF
chmod +x ~/.xinitrc

echo "🔁 Configuring .bash_profile to auto-start X..."
if ! grep -Fxq "startx" ~/.bash_profile 2>/dev/null; then
  echo -e '\nif [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then\n  startx\nfi' >> ~/.bash_profile
fi

echo "🔧 Creating systemd service for kiosk mode..."
SERVICE_FILE="/etc/systemd/system/kiosk.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Kivy App Kiosk
After=graphical.target

[Service]
ExecStart=/usr/bin/python3 /home/$USER/FingerPrintApp/main.py
Restart=always
User=$USER
Environment=DISPLAY=:0
Environment=XDG_RUNTIME_DIR=/run/user/1000

[Install]
WantedBy=graphical.target
EOL

echo "✅ Enabling kiosk service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service

echo "🎉 Setup complete. Rebooting now..."
sudo reboot

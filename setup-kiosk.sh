#!/bin/bash

set -e

echo "🛠️  Setting up kiosk environment..."

# 1. Install required packages
sudo apt update
sudo apt install -y python3-full python3-venv python3-pip git libegl1 libgles2 mesa-utils xinit

# 2. Create Python virtual environment
cd /home/Admin
if [ ! -d fingerprint-env ]; then
  python3 -m venv fingerprint-env
fi
source fingerprint-env/bin/activate

# 3. Install Python dependencies
cd /home/Admin/FingerPrintApp
if [ -f requirements.txt ]; then
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "⚠️  No requirements.txt found!"
fi

# 4. Create kiosk systemd service
echo "📺 Creating systemd kiosk service..."
cat <<EOF | sudo tee /etc/systemd/system/kiosk.service
[Unit]
Description=Kivy App Kiosk
After=network.target

[Service]
Type=simple
ExecStart=/home/Admin/fingerprint-env/bin/python /home/Admin/FingerPrintApp/main.py
WorkingDirectory=/home/Admin/FingerPrintApp
Restart=on-failure
RestartSec=5
User=Admin
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/Admin/.Xauthority

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl restart kiosk.service

# 5. Enable auto-login to console
echo "🔐 Enabling auto-login for user Admin..."
sudo raspi-config nonint do_boot_behaviour B2

# 6. Optional performance tweaks
echo "⚡ Applying optional performance tweaks..."
sudo sed -i '/^#.*disable_splash/ d' /boot/config.txt
echo "disable_splash=1" | sudo tee -a /boot/config.txt

# 7. Optional X11 auto-start via .bash_profile (Lite only)
echo "🪟 Auto-starting X11 and Kivy app at login..."
if ! grep -q "xinit" /home/Admin/.bash_profile 2>/dev/null; then
  echo "[[ -z \$DISPLAY && \$XDG_VTNR -eq 1 ]] && xinit" >> /home/Admin/.bash_profile
fi

# 8. Create minimal .xinitrc for kiosk
cat <<EOF > /home/Admin/.xinitrc
#!/bin/bash
exec /home/Admin/fingerprint-env/bin/python /home/Admin/FingerPrintApp/main.py
EOF
chmod +x /home/Admin/.xinitrc

echo "✅ Kiosk setup complete. Reboot to test:"
echo "    sudo reboot"

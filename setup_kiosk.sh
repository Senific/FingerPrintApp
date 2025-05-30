#!/bin/bash

echo "🔧 Step 1: Enable auto login for user 'admin'..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
cat <<EOF | sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin admin --noclear %I \$TERM
EOF

echo "🔧 Step 2: Create systemd service to launch your app..."
SERVICE_PATH="/etc/systemd/system/fingerprint-kiosk.service"

sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Start FingerPrintApp in kiosk mode
After=network.target graphical.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/FingerPrintApp
ExecStart=/home/admin/my_venv/bin/python main.py
Restart=always
RestartSec=2
StandardOutput=journal
StandardError=journal
Environment=KIVY_METRICS_FPS=1
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable fingerprint-kiosk.service

echo "🔧 Step 3: Disable boot logs and shell prompts..."

# Disable kernel boot messages
sudo sed -i 's/$/ quiet loglevel=0 logo.nologo vt.global_cursor_default=0/' /boot/cmdline.txt

# Mask getty to hide login prompts
sudo systemctl mask getty@tty1.service

# Disable Ctrl+Alt+F key switching
sudo bash -c 'echo "keyboard-setup keyboard-setup/layoutcode string us\nkeyboard-setup keyboard-setup/modelcode string pc105\nkeyboard-setup keyboard-setup/variantcode string" | debconf-set-selections'

echo "✅ Setup Complete. Please reboot to test the kiosk mode."

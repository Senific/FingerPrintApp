#!/bin/bash

APP_PATH="/home/Admin/FingerPrintApp/main.py"
START_SCRIPT="/home/Admin/start_kiosk.sh"
XINITRC="/home/Admin/.xinitrc"
SERVICE_FILE="/etc/systemd/system/kiosk.service"

# Check correct user
if [ "$USER" != "Admin" ]; then
  echo "❌ Please run this as user: Admin"
  exit 1
fi

echo "🔄 Updating system..."
sudo apt update

echo "📦 Installing minimal X11 and git packages..."
sudo apt install -y xserver-xorg x11-xserver-utils xinit xterm git

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

echo "🛠️ Creating kiosk.service..."
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

echo "🔁 Reloading and enabling kiosk.service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable kiosk.service
sudo systemctl start kiosk.service

echo "🔐 Enabling autologin for Admin on tty1..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d

sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin Admin --noclear %I \$TERM
EOF

echo "🚫 Disabling login prompts on other virtual terminals (tty2–tty6)..."
for tty in {2..6}; do
    sudo systemctl disable getty@tty$tty.service
done

echo "🧹 Optional: Clean up boot messages for silent boot (editing /boot/cmdline.txt)"
sudo sed -i 's/$/ quiet loglevel=0 console=tty3/' /boot/cmdline.txt

echo "✅ Setup complete. Reboot to apply all settings."

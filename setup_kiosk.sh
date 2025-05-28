#!/bin/bash

APP_PATH="/home/Admin/FingerPrintApp/main.py"
START_SCRIPT="/home/Admin/start_kiosk.sh"
XINITRC="/home/Admin/.xinitrc"
SERVICE_FILE="/etc/systemd/system/kiosk.service"

# ✅ Ensure this script is run as the correct user
if [ "$USER" != "Admin" ]; then
  echo "❌ Please run this as user: Admin"
  exit 1
fi

echo "🔄 Updating system..."
sudo apt update

echo "📦 Installing X11, Python, and Kivy system-wide..."
sudo apt install -y xserver-xorg x11-xserver-utils xinit xterm python3-pip
sudo apt install -y python3-kivy

echo "📝 Creating start script..."
cat <<EOF > "$START_SCRIPT"
#!/bin/bash
export DISPLAY=:0
export XAUTHORITY=/home/Admin/.Xauthority

echo "🚀 Launching Kivy App..."
python3 "$APP_PATH" 2>&1 | tee /home/Admin/kiosk_app.log
EOF

chmod +x "$START_SCRIPT"

echo "📝 Creating .xinitrc..."
cat <<EOF > "$XINITRC"
#!/bin/bash
exec $START_SCRIPT
EOF

chmod +x "$XINITRC"

echo "🛠️ Creating systemd kiosk.service..."
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

echo "🧹 Optional: Clean boot message line in /boot/cmdline.txt"
sudo sed -i 's/$/ quiet loglevel=0 console=tty3/' /boot/cmdline.txt

echo "✅ Kiosk setup complete. Reboot to start the Kivy app on boot."

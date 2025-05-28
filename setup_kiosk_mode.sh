#!/bin/bash
set -e

APP_PATH="/home/Admin/main.py"

echo "🛠️ Creating fbcp systemd service..."
sudo tee /etc/systemd/system/fbcp.service > /dev/null <<EOF
[Unit]
Description=Framebuffer copy for ILI9486
After=multi-user.target

[Service]
ExecStart=/home/Admin/fbcp-ili9341/build/fbcp-ili9341
Restart=always
User=Admin

[Install]
WantedBy=multi-user.target
EOF

echo "🛠️ Creating systemd service for Kivy app..."
sudo tee /etc/systemd/system/kivyapp.service > /dev/null <<EOF
[Unit]
Description=Kivy App Kiosk
After=fbcp.service

[Service]
ExecStart=/home/Admin/kivy_venv/bin/python ${APP_PATH}
WorkingDirectory=/home/Admin
Environment=FRAMEBUFFER=/dev/fb1
User=Admin
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "⚙️ Configuring system for kiosk mode..."

# Hide boot text and logo
sudo sed -i 's/$/ console=tty3 quiet splash loglevel=0 logo.nologo vt.global_cursor_default=0/' /boot/cmdline.txt

# Disable login and Ctrl+Alt+Del
sudo systemctl disable getty@tty1.service
sudo systemctl mask ctrl-alt-del.target
sudo systemctl mask getty@tty2.service getty@tty3.service getty@tty4.service
sudo systemctl mask getty@tty5.service getty@tty6.service

# Enable services
sudo systemctl enable fbcp.service
sudo systemctl enable kivyapp.service

echo "👑 Ensuring full permissions for user 'Admin'..."

# Ensure Admin is in admin groups
sudo usermod -aG sudo,adm,dialout,cdrom,audio,video,plugdev Admin

# Own everything in Admin's home
sudo chown -R Admin:Admin /home/Admin

# Set permissions on removable drives
for mount in /media/Admin/*; do
    sudo chown -R Admin:Admin "$mount"
    sudo chmod -R u+rwX "$mount"
done

echo "✅ Admin user fully configured and kiosk mode ready. Please reboot."

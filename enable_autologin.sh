#!/bin/bash

set -e

echo "🔧 Enabling auto-login for user: admin..."

# Create override directory if it doesn't exist
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d

# Write the override configuration
sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null <<EOL
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin admin --noclear %I \$TERM
EOL

# Reload systemd and restart the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart getty@tty1

echo "✅ Auto-login enabled for user 'admin'."
echo "🔁 Please reboot to test: sudo reboot"

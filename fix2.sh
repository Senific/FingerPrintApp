#!/bin/bash

echo "🚫 Disabling console on /dev/fb1 for Kivy kiosk..."

# Step 1: Modify /boot/cmdline.txt
echo "📝 Updating cmdline.txt..."
sudo sed -i -E 's/(console=tty1|console=serial0,[0-9]+|fbcon=map:[0-9]+|fbcon=font:[^ ]+)//g' /boot/cmdline.txt
sudo sed -i 's/$/ fbcon=map:10 fbcon=font:VGA8x8 console=tty3/' /boot/cmdline.txt

# Step 2: Disable getty terminals
echo "🔇 Disabling all terminal logins on tty1-tty6..."
for tty in {1..6}; do
  sudo systemctl disable getty@tty$tty.service
done

# Step 3: Reload systemd
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# Step 4: Confirm framebuffer devices
echo "🖥️ Framebuffers:"
ls -l /dev/fb*

echo "✅ All done. Rebooting now to apply..."
sudo reboot

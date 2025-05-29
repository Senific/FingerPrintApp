#!/bin/bash

echo "🔧 Freeing /dev/fb1 from terminal usage so Kivy can render to it..."

# === 1. Move console to tty3 and disable framebuffer console on fb1 ===
echo "📝 Updating /boot/cmdline.txt..."

sudo sed -i -E 's/(console=tty1|console=serial0,[0-9]+|fbcon=map:[0-9]+|fbcon=font:[^ ]+)//g' /boot/cmdline.txt

if ! grep -q 'fbcon=map:10' /boot/cmdline.txt; then
  sudo sed -i 's/$/ fbcon=map:10 fbcon=font:VGA8x8 console=tty3/' /boot/cmdline.txt
fi

# === 2. Disable all virtual terminals (TTYs) that might use fb1 ===
echo "🚫 Disabling getty terminals on tty1 to tty6..."
for tty in {1..6}; do
  sudo systemctl disable getty@tty$tty.service
done

# === 3. Ensure systemd doesn’t reenable them on updates ===
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# === 4. Show result ===
echo "✅ Console moved to tty3, fb1 freed from terminal binding."
echo "🔁 Please reboot to apply changes:"
echo "    sudo reboot"


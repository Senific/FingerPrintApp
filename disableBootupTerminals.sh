#!/bin/bash
set -e

BOOT_CMDLINE="/boot/cmdline.txt"
TTY1_SERVICE="getty@tty1.service"

echo "Backing up current cmdline.txt..."
sudo cp "$BOOT_CMDLINE" "${BOOT_CMDLINE}.bak"

echo "Updating cmdline.txt to hide boot messages and move console to tty3..."
# Remove any existing console=tty1, quiet, splash options first
sudo sed -i 's/console=tty1[^ ]*//g' "$BOOT_CMDLINE"
sudo sed -i 's/quiet//g' "$BOOT_CMDLINE"
sudo sed -i 's/splash//g' "$BOOT_CMDLINE"

# Append new options to the end of the line (all in one line)
sudo sed -i '1 s/$/ console=tty3 quiet splash loglevel=3 vt.global_cursor_default=0/' "$BOOT_CMDLINE"

echo "Disabling getty@tty1.service to hide login prompt on tty1..."
sudo systemctl disable "$TTY1_SERVICE"
sudo systemctl stop "$TTY1_SERVICE"

echo "✅ Boot messages hidden and tty1 login prompt disabled."
echo "Please reboot your Raspberry Pi to apply changes."

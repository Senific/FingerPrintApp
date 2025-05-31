#!/bin/bash

set -e

USER_HOME="/home/admin"
APP_DIR="$USER_HOME/FingerPrintApp"
MAIN_PY="$APP_DIR/main.py"
XINITRC="$USER_HOME/.xinitrc"

echo "🖱️ Installing unclutter..."
sudo apt update
sudo apt install -y unclutter

echo "🔧 Creating invisible cursor config for X11..."
sudo mkdir -p /usr/share/X11/xorg.conf.d
sudo tee /usr/share/X11/xorg.conf.d/99-hide-cursor.conf > /dev/null <<EOL
Section "Device"
    Identifier "Builtin Graphics"
    Driver "fbdev"
    Option "HWCursor" "false"
EndSection

Section "ServerFlags"
    Option "BlankTime" "0"
    Option "StandbyTime" "0"
    Option "SuspendTime" "0"
    Option "OffTime" "0"
    Option "AIGLX" "false"
EndSection
EOL

echo "✅ X11 cursor rendering disabled."

echo "🧠 Ensuring Kivy disables cursor in main.py..."
if ! grep -q "Config.set('modules', 'cursor', '')" "$MAIN_PY"; then
    sed -i "1ifrom kivy.config import Config\nConfig.set('modules', 'cursor', '')\n" "$MAIN_PY"
    echo "✅ Kivy cursor disabled"
else
    echo "ℹ️ Kivy cursor already disabled"
fi

echo "🛠️ Adding unclutter to .xinitrc (instant hide)..."
if ! grep -q "unclutter" "$XINITRC"; then
    sed -i '1iunclutter -idle 0 -root &' "$XINITRC"
    echo "✅ unclutter added to $XINITRC"
else
    echo "ℹ️ unclutter already present in $XINITRC"
fi

echo "🔁 Done. Rebooting now to apply full cursor hiding..."
sudo reboot

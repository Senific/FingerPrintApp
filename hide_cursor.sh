#!/bin/bash

set -e

USER_HOME="/home/admin"
APP_DIR="$USER_HOME/FingerPrintApp"
MAIN_PY="$APP_DIR/main.py"
XINITRC="$USER_HOME/.xinitrc"

echo "🖱️ Installing unclutter..."
sudo apt update
sudo apt install -y unclutter

echo "🛠️ Updating .xinitrc to hide mouse cursor..."
if ! grep -q "unclutter" "$XINITRC"; then
    sed -i '1iunclutter -idle 0 -root &' "$XINITRC"
    echo "✅ unclutter line added to $XINITRC"
else
    echo "ℹ️ unclutter already present in $XINITRC"
fi

echo "🧠 Ensuring Kivy cursor is disabled in main.py..."
if ! grep -q "Config.set('modules', 'cursor', '')" "$MAIN_PY"; then
    sed -i "1ifrom kivy.config import Config\nConfig.set('modules', 'cursor', '')\n" "$MAIN_PY"
    echo "✅ Cursor module disabled in Kivy main.py"
else
    echo "ℹ️ Kivy cursor already disabled in main.py"
fi

echo "🎉 Mouse cursor will now be completely hidden after reboot!"

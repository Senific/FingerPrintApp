#!/bin/bash

APP_DIR="/home/Admin/FingerPrintApp"
cd "$APP_DIR" || {
  echo "❌ Cannot find application directory: $APP_DIR"
  exit 1
}


echo "🔄 Pulling latest code from Git..."
git reset --hard
git pull origin main


# === STEP 2: Activate and install Python dependencies ===
echo "Activating virtual environment..."
source "$HOME/my_venv/bin/activate"

# Optional: If you have a requirements.txt and want to install system-wide
if [ -f requirements.txt ]; then
  echo "📦 Installing dependencies system-wide..."
  pip3 install -r requirements.txt
fi


echo "💀 Killing old app instances..."
pkill -f main.py

echo "💀 Killing old X server if running..."
pkill Xorg

echo "🚀 Starting X server and app..."
startx &

echo "✅ Update complete."

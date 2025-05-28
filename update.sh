#!/bin/bash

APP_DIR="/home/Admin/FingerPrintApp"
cd "$APP_DIR" || {
  echo "❌ Cannot find application directory: $APP_DIR"
  exit 1
}

echo "🔄 Pulling latest code from Git..."
git reset --hard
git pull origin main

# Optional: If you have a requirements.txt and want to install system-wide
if [ -f requirements.txt ]; then
  echo "📦 Installing dependencies system-wide..."
  pip3 install --user -r requirements.txt
fi

echo "🔁 Restarting kiosk.service..."
sudo systemctl restart kiosk.service

echo "✅ Update complete."

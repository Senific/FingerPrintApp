#!/bin/bash

set -e

APP_DIR="/home/admin/FingerPrintApp"
VENV_PATH="/home/admin/senific_env"
BRANCH="main"

echo "🔧 Updating FingerPrintApp..."

# Navigate to project folder
cd "$APP_DIR"

# Reset and pull latest from Git
echo "📦 Performing git hard reset and pull..."
git reset --hard
git clean -fd
git checkout $BRANCH
git pull origin $BRANCH

# Activate virtual environment
echo "🐍 Installing new/updated Python dependencies..."
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
deactivate

# Restart the app (assuming .bash_profile/startx handles app restart)
echo "🔁 Restarting app..."
pkill -f startx || true
sleep 2

echo "✅ Update complete. App will auto-relaunch via login/startx."

#!/bin/bash

set -e

APP_DIR="/home/admin/FingerPrintApp"
VENV_PATH="/home/admin/senific_env"
BRANCH="main"

echo "🔧 Updating FingerPrintApp..."

cd "$APP_DIR"

echo "📦 Git reset and pull..."
git reset --hard
git clean -fd
git checkout $BRANCH
git pull origin $BRANCH

echo "🐍 Installing updated requirements..."
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
deactivate

echo "🔁 Restarting app..."
pkill -f startx || true
sleep 2
sudo -u admin bash -c 'DISPLAY=:0 startx &' > /dev/null 2>&1

echo "✅ Update + restart complete!"

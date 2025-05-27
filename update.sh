#!/bin/bash
APP_DIR="/home/Admin/FingerPrintApp"
cd "$APP_DIR" || exit

# Pull latest changes
git reset --hard
git pull origin main

# Reinstall dependencies if requirements.txt changes (optional)
# source ../fingerprint-env/bin/activate
# pip install -r requirements.txt

# Restart the kiosk service
sudo systemctl restart kiosk.service

#!/bin/bash

set -e

echo "🔧 Step 1: Setup virtual environment outside repo..."
ENV_PATH="/home/admin/senific_env"
APP_PATH="/home/admin/FingerPrintApp"
PYTHON_BIN="/usr/bin/python3"

if [ ! -d "$ENV_PATH" ]; then
    $PYTHON_BIN -m venv "$ENV_PATH"
    echo "✅ Virtual environment created at $ENV_PATH"
else
    echo "⚠️ Virtual environment already exists at $ENV_PATH"
fi

echo "🔧 Step 2: Activate environment and install requirements..."
source "$ENV_PATH/bin/activate"

pip install --upgrade pip
pip install kivy pillow

deactivate
echo "✅ Dependencies installed."

echo "🔧 Step 3: Create systemd service..."

SERVICE_FILE="/etc/systemd/system/fingerprint-kiosk.service"

sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=Start FingerPrintApp in kiosk mode
After=network.target

[Service]
User=admin
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=$APP_PATH
ExecStart=$ENV_PATH/bin/python $APP_PATH/main.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/fingerprint_app.log
StandardError=append:/var/log/fingerprint_app.log

[Install]
WantedBy=multi-user.target
EOL

echo "✅ Service created at $SERVICE_FILE"

echo "🔧 Step 4: Enable and start the service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable fingerprint-kiosk.service
sudo systemctl restart fingerprint-kiosk.service

echo "✅ App will now auto-start on reboot and auto-restart if it crashes."
echo "📄 Logs will be available at /var/log/fingerprint_app.log"

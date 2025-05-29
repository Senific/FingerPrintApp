#!/bin/bash

set -e

APP_DIR="/home/admin/FingerPrintApp"
VENV_DIR="/home/my_venv"
PYTHON="$VENV_DIR/bin/python"
SERVICE_FILE="/etc/systemd/system/fingerprintapp.service"

echo "🔧 Step 1: Create or verify virtual environment..."
if [ ! -f "$PYTHON" ]; then
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at $VENV_DIR"
fi

echo "📦 Step 2: Activate venv and install Kivy dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install kivy

echo "🖥️ Step 3: Verify 3.5\" ILI9486 framebuffer..."
if [ ! -e /dev/fb1 ]; then
    echo "❌ /dev/fb1 not found. Please ensure your ILI9486 driver is installed via /boot/config.txt."
    exit 1
fi

echo "🛠️ Step 4: Create systemd service file..."

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=FingerPrintApp Kivy Kiosk Service
After=network.target

[Service]
User=admin
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON $APP_DIR/main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=SDL_FBDEV=/dev/fb1
Environment=KIVY_BCM_DISPMANX_ID=2
Environment=KIVY_NO_ARGS=1
Environment=KIVY_METRICS_DENSITY=1
Environment=KIVY_GL_BACKEND=gl
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service created at $SERVICE_FILE"

echo "🔁 Step 5: Reload systemd and enable the service..."
sudo systemctl daemon-reload
sudo systemctl enable fingerprintapp.service
sudo systemctl restart fingerprintapp.service

echo "🧹 Step 6: Disable desktop boot and ensure kiosk mode..."
sudo systemctl set-default multi-user.target

echo "✅ Setup complete. App will now start on boot in kiosk mode."
systemctl status fingerprintapp.service

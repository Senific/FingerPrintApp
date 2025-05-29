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

echo "🖥️ Step 3: Configure environment for 3.5\" ILI9486 LCD..."

# Set environment variables Kivy uses to point to the LCD (usually fb1)
ENV_FILE="/home/admin/.kivy_env"
cat <<EOF > "$ENV_FILE"
export KIVY_BCM_DISPMANX_ID=2
export KIVY_NO_ARGS=1
export KIVY_METRICS_DENSITY=1
export KIVY_GL_BACKEND=gl
export FRAMEBUFFER=/dev/fb1
export SDL_FBDEV=/dev/fb1
EOF

# Add to .bash_profile if not already
if ! grep -q ".kivy_env" /home/admin/.bash_profile; then
    echo "source ~/.kivy_env" >> /home/admin/.bash_profile
fi

echo "🛠️ Step 4: Create systemd service..."

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=FingerPrintApp Kivy Kiosk Service
After=network.target

[Service]
User=admin
WorkingDirectory=$APP_DIR
ExecStart=/home/my_venv/bin/python $APP_DIR/main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
StandardOutput=journal
StandardError=journal
EnvironmentFile=$ENV_FILE

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service created."

echo "🔁 Step 5: Reload systemd and enable the app..."
sudo systemctl daemon-reload
sudo systemctl enable fingerprintapp.service
sudo systemctl restart fingerprintapp.service

echo "🧹 Step 6: Disable desktop boot (if enabled)..."
sudo systemctl set-default multi-user.target

echo "✅ All done! App will now launch full-screen on boot using the LCD."

systemctl status fingerprintapp.service

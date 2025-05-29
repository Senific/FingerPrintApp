#!/bin/bash
set -e

# === CONFIGURATION ===
USER="admin"
APP_DIR="FingerPrintApp"
VENV_DIR="$HOME/my_venv"
PYTHON="$VENV_DIR/bin/python"
MAIN_SCRIPT="$APP_DIR/main.py"
LOG_FILE="$HOME/fingerprintapp.log"
SERVICE_NAME="fingerprintapp"

echo "----------------------------------------"
echo "1. Enable ILI9486 Touchscreen Driver"
echo "----------------------------------------"

# Add LCD overlay to config.txt (if not already present)
if ! grep -q "dtoverlay=ili9486" /boot/config.txt; then
    echo "Adding ILI9486 driver overlay..."
    echo "dtoverlay=ili9486,miso=off,rotate=270,speed=16000000,fps=30" | sudo tee -a /boot/config.txt
    echo "framebuffer_width=480" | sudo tee -a /boot/config.txt
    echo "framebuffer_height=320" | sudo tee -a /boot/config.txt
fi

echo "----------------------------------------"
echo "2. Install Minimal X11 & Kivy Dependencies"
echo "----------------------------------------"

sudo apt-get update
sudo apt-get install -y \
    python3-dev python3-pip python3-virtualenv \
    libgl1-mesa-dev libgles2-mesa-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev libgstreamer1.0 libmtdev-dev \
    xserver-xorg xinit x11-xserver-utils

echo "----------------------------------------"
echo "3. Create .xinitrc to Auto-launch Kivy App"
echo "----------------------------------------"

# Create .xinitrc script that will launch the Kivy app in a loop
sudo -u $USER bash -c "cat > //$HOME/.xinitrc" << EOF
#!/bin/bash
# Disable screen blanking and power saving
xset -dpms
xset s off
xset s noblank

# Run app in a loop, logging output
while true; do
    echo "Starting Kivy app..." >> "$LOG_FILE"
    date >> "$LOG_FILE"
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    $PYTHON "$MAIN_SCRIPT" >> "$LOG_FILE" 2>&1
    echo "App crashed or exited. Restarting in 3 seconds..." >> "$LOG_FILE"
    sleep 3
done
EOF

chmod +x /$HOME/.xinitrc

echo "----------------------------------------"
echo "4. Set up Auto-login on TTY1"
echo "----------------------------------------"

# Auto-login user on tty1 so startx can run
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d

sudo bash -c "cat > /etc/systemd/system/getty@tty1.service.d/override.conf" << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $USER --noclear %I \$TERM
EOF

echo "----------------------------------------"
echo "5. Launch X on Login via .bash_profile"
echo "----------------------------------------"

# Ensure startx runs only on tty1 and not in SSH
sudo -u $USER bash -c "cat > /$HOME/.bash_profile" << EOF
if [[ -z \$DISPLAY ]] && [[ \$(tty) = /dev/tty1 ]]; then
    startx
fi
EOF

echo "----------------------------------------"
echo "6. Prepare Log File for App Output"
echo "----------------------------------------"

touch "$LOG_FILE"
chown $USER:$USER "$LOG_FILE"

echo "----------------------------------------"
echo "7. Enable All Configurations and Reboot"
echo "----------------------------------------"

echo "Setup complete. The system will now reboot."
echo "On boot, it will auto-login, launch X, and start your Kivy app."

sleep 5
sudo reboot

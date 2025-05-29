#!/bin/bash
set -e

# === CONFIGURATION ===
USER="admin"
HOME_DIR="/home/$USER"
APP_DIR="$HOME_DIR/FingerPrintApp"
VENV_DIR="$APP_DIR/my_venv"
PYTHON="$VENV_DIR/bin/python"
MAIN_SCRIPT="$APP_DIR/main.py"
LOG_FILE="$HOME_DIR/fingerprintapp.log"
XINITRC="$HOME_DIR/.xinitrc"

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
    xserver-xorg xinit x11-xserver-utils unclutter

echo "----------------------------------------"
echo "3. Create .xinitrc to Auto-launch Kivy App"
echo "----------------------------------------"

# Create .xinitrc in user's home directory
sudo -u $USER bash -c "cat > $XINITRC" << 'EOF'
#!/bin/bash

# Disable screen blanking and power saving
xset -dpms
xset s off
xset s noblank

# Hide the mouse cursor
unclutter -idle 0.1 -root &

# Log and run Kivy app in a loop
while true; do
    echo "Starting Kivy app..." >> "$HOME/fingerprintapp.log"
    date >> "$HOME/fingerprintapp.log"
    cd "$HOME/FingerPrintApp"
    source "$HOME/FingerPrintApp/my_venv/bin/activate"
    "$HOME/FingerPrintApp/my_venv/bin/python" "$HOME/FingerPrintApp/main.py" >> "$HOME/fingerprintapp.log" 2>&1
    echo "App crashed or exited. Restarting in 3 seconds..." >> "$HOME/fingerprintapp.log"
    sleep 3
done
EOF

chmod +x "$XINITRC"
chown $USER:$USER "$XINITRC"

echo "----------------------------------------"
echo "4. Set up Auto-login on TTY1"
echo "----------------------------------------"

sudo mkdir -p /etc/systemd/system/getty@tty1.service.d

sudo bash -c "cat > /etc/systemd/system/getty@tty1.service.d/override.conf" << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $USER --noclear %I \$TERM
EOF

echo "----------------------------------------"
echo "5. Launch X on Login via .bash_profile"
echo "----------------------------------------"

sudo -u $USER bash -c "cat > $HOME_DIR/.bash_profile" << EOF
if [[ -z \$DISPLAY ]] && [[ \$(tty) = /dev/tty1 ]]; then
    startx
fi
EOF

chown $USER:$USER "$HOME_DIR/.bash_profile"

echo "----------------------------------------"
echo "6. Prepare Log File for App Output"
echo "----------------------------------------"

touch "$LOG_FILE"
chown $USER:$USER "$LOG_FILE"

echo "----------------------------------------"
echo "7. Check If main.py Exists"
echo "----------------------------------------"

if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "⚠️ ERROR: $MAIN_SCRIPT not found!"
    echo "Please make sure your Kivy app main.py exists before rebooting."
    exit 1
fi

echo "----------------------------------------"
echo "8. Enable All Configurations and Reboot"
echo "----------------------------------------"

echo "✅ Setup complete. Rebooting now to apply changes..."
sleep 5
sudo reboot

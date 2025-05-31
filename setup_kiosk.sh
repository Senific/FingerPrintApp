#!/bin/bash

set -e

APP_DIR="/home/admin/FingerPrintApp"
VENV_PATH="/home/admin/senific_env"
USER_NAME="admin"

echo "🔧 Step 1: Install X11 and kiosk tools..."
sudo apt update
sudo apt install -y --no-install-recommends \
    xserver-xorg xinit x11-xserver-utils xterm python3-tk unclutter

echo "✅ X11 installed."

echo "🔧 Step 2: Create .xinitrc with auto-restart loop..."
XINITRC_PATH="/home/$USER_NAME/.xinitrc"

cat > "$XINITRC_PATH" <<EOL
#!/bin/bash
xset s off
xset -dpms
xset s noblank
unclutter &

cd $APP_DIR
source $VENV_PATH/bin/activate

# Auto-restart loop on crash
while true; do
    echo "Launching FingerPrintApp at \$(date)" >> /tmp/kiosk_restart.log
    python main.py
    echo "App crashed or exited at \$(date)" >> /tmp/kiosk_restart.log
    sleep 2
done
EOL

chmod +x "$XINITRC_PATH"
chown $USER_NAME:$USER_NAME "$XINITRC_PATH"

echo "✅ .xinitrc with auto-restart loop created."

echo "🔧 Step 3: Enable startx on TTY1 login..."
BASH_PROFILE="/home/$USER_NAME/.bash_profile"
if [ ! -f "$BASH_PROFILE" ]; then
    touch "$BASH_PROFILE"
    chown $USER_NAME:$USER_NAME "$BASH_PROFILE"
fi

grep -q "startx" "$BASH_PROFILE" || cat >> "$BASH_PROFILE" <<'EOL'

# Auto-start X only on TTY1 (not over SSH)
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    startx
fi
EOL

echo "✅ Auto-start added to .bash_profile"

echo "🔁 Kiosk setup complete. Reboot to test!"

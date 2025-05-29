#!/bin/bash

TARGET_USER="admin"
APP_DIR="/home/$TARGET_USER/FingerPrintApp"
APP_PATH="$APP_DIR/main.py"
VENV_DIR="/home/$TARGET_USER/my_venv"
START_SCRIPT="/home/$TARGET_USER/start_app.sh"
XINITRC="/home/$TARGET_USER/.xinitrc"
BASH_PROFILE="/home/$TARGET_USER/.bash_profile"

# Check if script is run as the correct user
if [ "$(whoami)" != "$TARGET_USER" ]; then
  echo "❌ Please run this script as user: $TARGET_USER"
  exit 1
fi

echo "🔄 Updating system and installing minimal X11 stack..."
sudo apt update
sudo apt install -y \
  xserver-xorg \
  x11-xserver-utils \
  xinit \
  xterm \
  git \
  python3 \
  python3-venv \
  python3-pip \
  --no-install-recommends

echo "🧪 Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "📦 Installing dependencies from requirements.txt..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
[ -f "$APP_DIR/requirements.txt" ] && pip install -r "$APP_DIR/requirements.txt"
deactivate

echo "📝 Creating start_app.sh to run app in venv on DISPLAY=:0..."
cat <<EOF > "$START_SCRIPT"
#!/bin/bash
export DISPLAY=:0
source "$VENV_DIR/bin/activate"
python3 "$APP_PATH"
EOF
chmod +x "$START_SCRIPT"

echo "📝 Creating .xinitrc to launch start_app.sh silently..."
cat <<EOF > "$XINITRC"
#!/bin/bash
xset -dpms      # Disable energy saving
xset s off      # Disable screen saver
xset s noblank  # Prevent blanking
exec $START_SCRIPT
EOF
chmod +x "$XINITRC"

echo "🔁 Ensuring startx runs automatically on tty1 login..."
if ! grep -q "startx" "$BASH_PROFILE"; then
cat <<EOF >> "$BASH_PROFILE"

# Auto-launch X if not running and on tty1
if [[ -z "\$DISPLAY" ]] && [[ \$(tty) == /dev/tty1 ]]; then
  startx
fi
EOF
fi

echo "🔐 Enabling autologin for $TARGET_USER on tty1..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $TARGET_USER --noclear %I \$TERM
EOF

echo "🖥️ Setting up X11 to use ILI9486 framebuffer (/dev/fb1)..."
sudo mkdir -p /etc/X11/xorg.conf.d
sudo tee /etc/X11/xorg.conf.d/99-fbdev.conf > /dev/null <<EOF
Section "Device"
    Identifier  "FBDEV"
    Driver      "fbdev"
    Option      "fbdev" "/dev/fb1"
EndSection
EOF

echo "🛑 Disabling getty prompts on unused ttys (2-6)..."
for tty in {2..6}; do
  sudo systemctl disable getty@tty$tty.service
done

echo "🧹 Cleaning up console messages and enabling silent boot..."
sudo sed -i 's/$/ quiet loglevel=0 console=tty3/' /boot/cmdline.txt
sudo sed -i 's/^/#/' /etc/profile.d/sshpwd.sh 2>/dev/null || true

echo "✅ Kiosk mode setup complete. Reboot to apply changes!"

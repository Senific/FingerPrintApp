#!/bin/bash

TARGET_USER="admin"
APP_DIR="/home/$TARGET_USER/FingerPrintApp"
APP_PATH="$APP_DIR/main.py"
VENV_DIR="/home/$TARGET_USER/my_venv"
START_SCRIPT="/home/$TARGET_USER/start_app.sh"
XINITRC="/home/$TARGET_USER/.xinitrc"
BASH_PROFILE="/home/$TARGET_USER/.bash_profile"

# Check correct user
if [ "$(whoami)" != "$TARGET_USER" ]; then
  echo "❌ Please run this script as user: $TARGET_USER"
  exit 1
fi

echo "🔄 Updating system and installing required packages..."
sudo apt update
sudo apt install -y xserver-xorg x11-xserver-utils xinit xterm git python3 python3-venv python3-pip

echo "🧹 Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "📦 Installing Python dependencies in virtual environment..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
if [ -f "$APP_DIR/requirements.txt" ]; then
  pip install -r "$APP_DIR/requirements.txt"
fi
deactivate

echo "📝 Creating start_app.sh to launch app inside venv..."
cat <<EOF > "$START_SCRIPT"
#!/bin/bash
export DISPLAY=:0
source "$VENV_DIR/bin/activate"
python3 "$APP_PATH"
EOF
chmod +x "$START_SCRIPT"

echo "📝 Creating .xinitrc to launch start_app.sh..."
cat <<EOF > "$XINITRC"
#!/bin/bash
export DISPLAY=:0
exec $START_SCRIPT
EOF
chmod +x "$XINITRC"

echo "🧠 Adding autostart of X in .bash_profile on tty1..."
cat <<EOF >> "$BASH_PROFILE"

# Auto-launch startx on tty1
if [[ -z "\$DISPLAY" ]] && [[ \$(tty) == /dev/tty1 ]]; then
  startx
fi
EOF

echo "🔐 Setting up autologin on tty1 for $TARGET_USER..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $TARGET_USER --noclear %I \$TERM
EOF

echo "🖥️ (Optional) Creating X11 config to use /dev/fb1 (ILI9486)..."
sudo mkdir -p /etc/X11/xorg.conf.d
sudo tee /etc/X11/xorg.conf.d/99-fbdev.conf > /dev/null <<EOF
Section "Device"
    Identifier  "FBDEV"
    Driver      "fbdev"
    Option      "fbdev" "/dev/fb1"
EndSection
EOF

echo "🚫 Disabling getty login prompts on tty2-tty6..."
for tty in {2..6}; do
  sudo systemctl disable getty@tty$tty.service
done

echo "🧹 Adding quiet boot to /boot/cmdline.txt..."
if ! grep -q "quiet loglevel=0 console=tty3" /boot/cmdline.txt; then
  sudo sed -i 's/$/ quiet loglevel=0 console=tty3/' /boot/cmdline.txt
fi

echo "✅ Setup complete! Reboot your Pi to test kiosk mode on LCD."

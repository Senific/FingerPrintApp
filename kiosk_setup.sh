#!/bin/bash

# ========= USER CONFIG =========
APP_MAIN="main.py"
APP_PATH="$(pwd)/$APP_MAIN"
USER_HOME="/home/$USER"
LOG_FILE="$USER_HOME/FingerPrintApp/kiosk_app.log"
FRAMEBUFFER="/dev/fb1"  # ILI9480 screen
SCREEN_RES="320x480"
# ==============================

# -------- CHECK --------
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run this as your Admin user (not root)"
    exit 1
fi

echo "🔧 Installing required packages..."
sudo apt update
sudo apt install -y --no-install-recommends \
    xserver-xorg \
    xinit \
    x11-xserver-utils \
    x11-xkb-utils \
    openbox \
    unclutter \
    fbi

echo "🖥️ Configuring X11 to use $FRAMEBUFFER..."
sudo mkdir -p /etc/X11/xorg.conf.d
sudo tee /etc/X11/xorg.conf.d/99-fbdev.conf >/dev/null <<EOF
Section "Device"
    Identifier  "LCD"
    Driver      "fbdev"
    Option      "fbdev" "$FRAMEBUFFER"
EndSection

Section "Monitor"
    Identifier "LCDMonitor"
    Option     "IgnoreEDID" "true"
EndSection

Section "Screen"
    Identifier "LCDScreen"
    Device     "LCD"
    Monitor    "LCDMonitor"
    DefaultDepth 24
    SubSection "Display"
        Depth 24
        Modes "$SCREEN_RES"
    EndSubSection
EndSection

Section "ServerLayout"
    Identifier "DefaultLayout"
    Screen "LCDScreen"
EndSection
EOF

echo "🧠 Creating ~/.xinitrc to auto-start app..."
cat > "$USER_HOME/.xinitrc" <<EOF
#!/bin/bash
xset s off
xset -dpms
xset s noblank
unclutter &
xmodmap ~/.Xmodmap &
openbox-session &
sleep 2
python3 "$APP_PATH" >> "$LOG_FILE" 2>&1
EOF

chmod +x "$USER_HOME/.xinitrc"

echo "🔒 Creating ~/.Xmodmap to disable keys..."
cat > "$USER_HOME/.Xmodmap" <<EOF
clear control
clear mod1
clear mod4
keycode  37 = NoSymbol  # Ctrl
keycode  64 = NoSymbol  # Alt
keycode 133 = NoSymbol  # Super/Meta
EOF

echo "⚙️ Disabling TTY switching..."
sudo sed -i 's/^#*NAutoVTs=.*/NAutoVTs=1/' /etc/systemd/logind.conf
sudo sed -i 's/^#*ReserveVT=.*/ReserveVT=0/' /etc/systemd/logind.conf
sudo sed -i 's/^#*HandlePowerKey=.*/HandlePowerKey=ignore/' /etc/systemd/logind.conf
sudo sed -i 's/^#*HandleSuspendKey=.*/HandleSuspendKey=ignore/' /etc/systemd/logind.conf
sudo sed -i 's/^#*HandleHibernateKey=.*/HandleHibernateKey=ignore/' /etc/systemd/logind.conf
sudo sed -i 's/^#*HandleLidSwitch=.*/HandleLidSwitch=ignore/' /etc/systemd/logind.conf
sudo systemctl restart systemd-logind

echo "💡 Enabling autostart on tty1..."
BASH_PROFILE="$USER_HOME/.bash_profile"
if ! grep -q "startx" "$BASH_PROFILE"; then
    echo 'if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then' >> "$BASH_PROFILE"
    echo '  startx' >> "$BASH_PROFILE"
    echo 'fi' >> "$BASH_PROFILE"
fi

echo "🔐 Ensuring passwordless sudo for Admin..."
if ! sudo grep -q "^$USER" /etc/sudoers; then
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/010_admin_nopasswd
    sudo chmod 440 /etc/sudoers.d/010_admin_nopasswd
fi

echo "🧹 Hiding boot messages..."
sudo sed -i 's/$/ console=tty3 quiet splash loglevel=0 logo.nologo vt.global_cursor_default=0/' /boot/cmdline.txt
sudo sed -i '/disable_splash/d' /boot/config.txt
echo 'disable_splash=1' | sudo tee -a /boot/config.txt

echo "📜 Setting log file..."
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

echo "✅ Setup complete! Reboot to launch into kiosk mode:"
echo "   sudo reboot"

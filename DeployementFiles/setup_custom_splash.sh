#!/bin/bash

# === Configuration ===
THEME_NAME="mysplash"
LOGO_NAME="splash.png"
THEME_DIR="/usr/share/plymouth/themes/$THEME_NAME"
SCRIPT_FILE="$THEME_DIR/$THEME_NAME.script"
PLYMOUTH_FILE="$THEME_DIR/$THEME_NAME.plymouth"

# === Get script's directory ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGO_SOURCE="$SCRIPT_DIR/$LOGO_NAME"

# === 1. Check for splash image ===
if [ ! -f "$LOGO_SOURCE" ]; then
  echo "❌ splash.png not found in the same folder as this script."
  exit 1
fi

echo "📦 Installing Plymouth..."
sudo apt update
sudo apt install -y plymouth plymouth-themes

echo "📁 Creating theme directory..."
sudo mkdir -p "$THEME_DIR"
sudo cp "$LOGO_SOURCE" "$THEME_DIR/"

echo "📝 Writing Plymouth theme file..."
sudo tee "$PLYMOUTH_FILE" > /dev/null <<EOF
[Plymouth Theme]
Name=My Splash
Description=Senific (PVT) Ltd / www.senific.com
ModuleName=script

[script]
ImageDir=$THEME_DIR
ScriptFile=$SCRIPT_FILE
EOF

echo "📝 Writing splash script..."
sudo tee "$SCRIPT_FILE" > /dev/null <<'EOF'
screen_width = Window.GetWidth();
screen_height = Window.GetHeight();
logo = Image("splash.png");
logo.SetPosition(screen_width / 2 - logo.GetWidth() / 2, screen_height / 2 - logo.GetHeight() / 2);
EOF

echo "🎨 Setting theme as default..."
sudo plymouth-set-default-theme -R "$THEME_NAME"

echo "🛠 Updating /boot/config.txt to disable Pi splash..."
sudo sed -i '/disable_splash/d' /boot/config.txt
echo "disable_splash=1" | sudo tee -a /boot/config.txt

echo "🛠 Updating /boot/cmdline.txt to suppress boot text..."
sudo sed -i 's/ quiet splash loglevel=0 logo.nologo vt.global_cursor_default=0//g' /boot/cmdline.txt
sudo sed -i 's/$/ quiet splash loglevel=0 logo.nologo vt.global_cursor_default=0/' /boot/cmdline.txt

echo "✅ Setup complete!"
echo "🔁 Reboot to see your custom splash screen:"
echo "    sudo reboot"

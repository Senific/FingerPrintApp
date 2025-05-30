sudo apt update
sudo apt install -y git

git clone https://github.com/Senific/FingerPrintApp.git
cd FingerPrintApp

chmod +x setup.sh
./setup.sh


git clone https://github.com/goodtft/LCD-show.git /home/admin/LCD-show
cd /home/admin/LCD-show
chmod +x LCD35-show

echo "=== Installing ILI9486 driver (will reboot) ==="
sudo ./LCD35-show


#!/bin/bash

# Define the path to the .bash_profile file
BASH_PROFILE="/home/Admin/.bash_profile"

# Write the required content to the file
cat << 'EOF' > "$BASH_PROFILE"
if [ "$(tty)" = "/dev/tty1" ]; then
    export FRAMEBUFFER=/dev/fb1
    export KIVY_BCM_DISPMANX_ID=2
    source /home/Admin/my_venv/bin/activate
    python /home/Admin/FingerPrintApp/main.py
fi
EOF

echo ".bash_profile has been created/updated at $BASH_PROFILE"

#!/bin/bash

PROFILE="$HOME/.profile"
LINE='[ -f ~/.bash_profile ] && . ~/.bash_profile'

# Check if the line is already in .profile
if grep -Fxq "$LINE" "$PROFILE"; then
    echo "Line already exists in $PROFILE"
else
    echo "$LINE" >> "$PROFILE"
    echo "Line added to $PROFILE"
fi


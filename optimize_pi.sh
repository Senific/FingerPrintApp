#!/bin/bash
# Raspberry Pi Optimization Script
# Purpose: Improve battery life and performance by disabling unused features

echo "🔧 Starting Raspberry Pi optimization..."

# ------------------------------------------
# 1. Disable Bluetooth (saves power if unused)
# ------------------------------------------
echo "➤ Disabling Bluetooth services..."
sudo systemctl disable hciuart 2>/dev/null
sudo systemctl disable bluetooth 2>/dev/null

# Disable Bluetooth overlay in config.txt
if ! grep -q "dtoverlay=disable-bt" /boot/config.txt; then
    echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt
fi

# ------------------------------------------
# 2. Disable Audio if unused (ALSA and drivers)
# ------------------------------------------
echo "➤ Disabling onboard audio..."
sudo systemctl disable alsa-utils 2>/dev/null

# Disable audio hardware in config
if ! grep -q "dtparam=audio=off" /boot/config.txt; then
    echo "dtparam=audio=off" | sudo tee -a /boot/config.txt
fi

# ------------------------------------------
# 3. Disable HDMI if unused (saves power when using SPI LCD)
# ------------------------------------------
echo "➤ Disabling HDMI output..."
/opt/vc/bin/tvservice -o

# Add HDMI off to startup (if not already present)
RCLOCAL="/etc/rc.local"
if ! grep -q "tvservice -o" $RCLOCAL; then
    sudo sed -i '/^exit 0/i /opt/vc/bin/tvservice -o' $RCLOCAL
fi

# ------------------------------------------
# 4. Disable unnecessary services
# ------------------------------------------
echo "➤ Disabling unnecessary services..."
DISABLE_SERVICES=(avahi-daemon triggerhappy dphys-swapfile cups)

for service in "${DISABLE_SERVICES[@]}"; do
    sudo systemctl disable "$service" 2>/dev/null
done

# ------------------------------------------
# 5. Prevent screen blanking (if using Kivy GUI)
# ------------------------------------------
echo "➤ Preventing screen blanking (for GUI apps)..."
if ! grep -q "consoleblank=0" /boot/cmdline.txt; then
    sudo sed -i 's/$/ consoleblank=0/' /boot/cmdline.txt
fi

# ------------------------------------------
# 6. (Optional) Underclock CPU/GPU to save power
# Comment this section out if performance is critical
# ------------------------------------------
# echo "➤ Underclocking CPU and GPU to save power..."
# CONFIG="/boot/config.txt"
# if ! grep -q "arm_freq=800" $CONFIG; then
#     echo -e "\n# Underclocking for battery saving" | sudo tee -a $CONFIG
#     echo "arm_freq=800" | sudo tee -a $CONFIG
#     echo "gpu_freq=200" | sudo tee -a $CONFIG
#     echo "core_freq=200" | sudo tee -a $CONFIG
# fi

# ------------------------------------------
# Done
# ------------------------------------------
echo "✅ Optimization complete. Please reboot to apply changes."

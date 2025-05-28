#Install LCD Driver
echo "=== Enabling SPI Interface ==="
sudo raspi-config nonint do_spi 0

echo "=== Installing required packages ==="
sudo apt update
sudo apt install -y git build-essential dkms raspberrypi-kernel-headers fbi

echo "=== Cloning LCD-show repository ==="
cd ~
if [ -d "LCD-show" ]; then
    rm -rf LCD-show
fi
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show

echo "=== Making script executable ==="
chmod +x LCD35-show

echo "=== Installing LCD driver for 3.5inch ILI9486 ==="
#sudo ./LCD35-show 270  # 270 = optional rotation (can be 0, 90, 180, 270)

echo "=== Done! Rebooting now... ==="
#end Install LCD Driver
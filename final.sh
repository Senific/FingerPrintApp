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
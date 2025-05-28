Do Following Steps on a Fresh Raspbery Pi 64bit lite OS Installation

sudo apt update
sudo apt install -y git

run install_lcd.sh


git clone https://github.com/Senific/FingerPrintApp.git
cd FingerPrintApp

chmod +x setup.sh
./setup.sh

chmod +x setup_kiosk.sh
./setup_kiosk.sh

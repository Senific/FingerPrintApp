Do Following Steps on a Fresh Raspbery Pi 64bit lite OS Installation

sudo apt update
sudo apt install -y git

sudo apt update
sudo apt install python3-venv python3-pip -y

python3 -m venv fingerprint-env
source fingerprint-env/bin/activate


git clone https://github.com/Senific/FingerPrintApp.git
cd FingerPrintApp
chmod +x install_kiosk.sh
./install_kiosk.sh

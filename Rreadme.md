Do Following Steps on a Fresh Raspbery Pi 64bit lite OS Installation

sudo apt update
sudo apt install -y git 

git clone https://github.com/Senific/FingerPrintApp.git
cd FingerPrintApp

chmod +x install_display.sh
./install_display.sh

chmod +x setup.sh
./setup.sh

chmod +x setup_kiosk.sh
./setup_kiosk.sh

chmod +x enable_autologin.sh
./enable_autologin.sh

#########
#Virtual Keyboard

source ~/senific_env/bin/activate
pip install kivy_garden
#garden install xkeyboard

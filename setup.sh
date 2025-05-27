#!binbash

# Automatically detect current username and paths
USER_HOME=$(eval echo ~$USER)
APP_DIR=$(pwd)
VENV_DIR=$APP_DIRfingerprint-env
PYTHON_BIN=$VENV_DIRbinpython
REQUIREMENTS_FILE=$APP_DIRrequirements.txt

echo Setting up FingerPrintApp
echo App Path        $APP_DIR
echo Virtual Env Dir $VENV_DIR

read -p Proceed with setup (yn)  confirm
if [[ $confirm != y ]]; then
    echo Setup aborted.
    exit 1
fi

# Update and install dependencies
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv

# Create and activate virtual environment
if [ ! -d $VENV_DIR ]; then
    echo Creating virtual environment...
    python3 -m venv $VENV_DIR
fi

# Activate and install Python dependencies
echo Installing Python dependencies...
$VENV_DIRbinpip install --upgrade pip
$VENV_DIRbinpip install -r $REQUIREMENTS_FILE

echo Setup complete.

# Ask to enable kiosk mode now
read -p Do you want to set this app to launch at boot in kiosk mode (yn)  kiosk_confirm
if [[ $kiosk_confirm == y ]]; then
    sudo bash $APP_DIRscriptssetup-kiosk.sh
fi

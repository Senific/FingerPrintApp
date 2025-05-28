#!/bin/bash

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$HOME/fingerprint-env"
PYTHON="$ENV_DIR/bin/python"
SERVICE_NAME="kiosk.service"

echo "🔧 Installing system dependencies..."
sudo apt update
sudo apt install -y git python3-full python3-venv python3-pip

echo "🐍 Creating virtual environment at $ENV_DIR..."
python3 -m venv "$ENV_DIR"

echo "📦 Installing Python dependencies..."
source "$ENV_DIR/bin/activate"
pip install --upgrade pip
pip install kivy




echo "🛠️ Done..."
 
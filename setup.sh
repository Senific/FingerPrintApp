# === STEP 2: Set up virtual environment ===
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip setuptools wheel Cython
pip install kivy[base] kivy[full]

# === STEP 3: Run the app ===
echo "Running the Kivy app..."
cd "$APP_DIR"
python3 main.py
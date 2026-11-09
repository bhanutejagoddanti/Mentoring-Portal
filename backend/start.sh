
#!/usr/bin/env bash

set -Eeuo pipefail

# Move to the backend directory (where this script is located)
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "======================================"
echo "   IITM BS Mentoring Portal Backend"
echo "======================================"

# Detect operating system
OS="$(uname -s)"

case "$OS" in
    Darwin*)
        echo "[INFO] Operating System: macOS"
        PYTHON_CMD="python3"
        ;;
    Linux*)
        echo "[INFO] Operating System: Linux"
        PYTHON_CMD="python3"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo "[INFO] Operating System: Windows (Git Bash)"
        PYTHON_CMD="python"
        ;;
    *)
        echo "[ERROR] Unsupported operating system: $OS"
        exit 1
        ;;
esac

# Check Python installation
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    echo "[ERROR] Python not found. Please install Python 3.10 or later."
    exit 1
fi

# Check Python version
"$PYTHON_CMD" -c '
import sys
if sys.version_info < (3, 10):
    print("Python 3.10 or later is required.")
    sys.exit(1)
print("Python version:", sys.version.split()[0])
'

# Create virtual environment if missing
if [ ! -f ".venv/pyvenv.cfg" ]; then
    echo "[INFO] Creating virtual environment..."
    "$PYTHON_CMD" -m venv .venv
else
    echo "[INFO] Existing virtual environment found."
fi

# Select virtual environment Python executable
case "$OS" in
    MINGW*|MSYS*|CYGWIN*)
        VENV_PYTHON=".venv/Scripts/python.exe"
        ;;
    *)
        VENV_PYTHON=".venv/bin/python"
        ;;
esac

if [ ! -x "$VENV_PYTHON" ]; then
    echo "[ERROR] Virtual environment Python executable not found."
    exit 1
fi

# Upgrade pip
echo "[INFO] Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "[INFO] Installing dependencies..."
    "$VENV_PYTHON" -m pip install -r requirements.txt
else
    echo "[ERROR] requirements.txt not found!"
    exit 1
fi

# Check environment configuration
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[INFO] Creating .env from .env.example..."
        cp .env.example .env
        echo "[WARNING] Configure your Supabase and OpenRouter credentials in backend/.env"
        echo "[WARNING] Run this script again after configuring .env."
        exit 1
    else
        echo "[WARNING] No .env or .env.example found."
    fi
fi

# Start Flask application
echo "======================================"
echo "[INFO] Starting Flask backend..."
echo "[INFO] URL: http://localhost:${PORT:-5001}"
echo "======================================"

exec "$VENV_PYTHON" app.py

#!/usr/bin/env bash
set -euo pipefail
# setup.sh - creates venv, installs deps, and offers to run the honeypot

VENV_DIR="${VENV_DIR:-venv}"
REQ_FILE="${REQ_FILE:-requirements.txt}"
PY="${PY:-python3}"

echo "== FTP Honeypot setup script =="
echo "Using Python: $(command -v $PY || true)"

# 1) create venv
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv in ./$VENV_DIR ..."
  $PY -m venv "$VENV_DIR"
else
  echo "Virtualenv already exists at ./$VENV_DIR"
fi

# 2) activate and install
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
echo "Upgrading pip..."
pip install --upgrade pip
echo "Installing from $REQ_FILE ..."
pip install -r "$REQ_FILE"

echo "Installation complete."
echo "To run the honeypot now:"
echo "  source $VENV_DIR/bin/activate"
echo "  python main.py"
read -p "Run the honeypot now (y/N)? " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
  python main.py
else
  echo "Done. Activate venv with: source $VENV_DIR/bin/activate"
fi

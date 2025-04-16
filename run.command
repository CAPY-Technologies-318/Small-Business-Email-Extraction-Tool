#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$DIR"

# Run the script
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 -m playwright install
python3 gui.py

#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$DIR"

# Run the script
python3 gui.py

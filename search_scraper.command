#!/bin/bash 

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
python3 search_scraper_gui.py

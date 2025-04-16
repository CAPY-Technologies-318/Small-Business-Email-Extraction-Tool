@echo off

REM Get the folder where this .bat file is located
set SCRIPT_DIR=%~dp0

REM Change to that folder
cd /d %SCRIPT_DIR%

REM Run the Python script
python gui.py


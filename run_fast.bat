@echo off
REM Start the FAST Python script with FAST binaries from C:\FAST (ASCII path)
setlocal enabledelayedexpansion

set PATH=C:\FAST\bin;%PATH%
set QT_QPA_PLATFORM_PLUGIN_PATH=C:\FAST\plugins

cd /d "%~dp0"
python Skript-US+Microscope.py

pause

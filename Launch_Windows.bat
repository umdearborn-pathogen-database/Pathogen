@echo off
REM Current directory
cd /d "%~dp0"

REM Sub-directory /Pathogen
cd Pathogen

REM Run using Python
python3 Pathogen.py

REM Pause to keep it open after running
pause
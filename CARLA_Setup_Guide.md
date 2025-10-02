# CARLA Setup and Usage Guide

## Overview
This guide explains how to start CARLA simulator and run Python client scripts for autonomous driving research and dataset creation.

## Prerequisites
- CARLA 0.9.16 downloaded and extracted to your desired location (e.g., `E:\CARLA_Latest`)
- Python 3.12.7 installed on your system
- Git for cloning the research repository
- GTX 1650 or better GPU (see hardware optimization guide)

## Repository Setup (New PC Installation)

### Step 1: Download and Setup CARLA
1. Download CARLA 0.9.16 from [official website](https://carla.org/2023/11/10/release-0.9.16/)
2. Extract to your desired location (e.g., `E:\CARLA_Latest`)

### Step 2: Clone Research Repository
```powershell
# Navigate to CARLA examples directory
cd E:\CARLA_Latest\PythonAPI\examples

# Clone the research repository
git clone https://github.com/MaheAlif/carla-dataset-creation.git .

# This will add all research files to your CARLA examples folder
```

### Step 3: Setup Python Environment
```powershell
# Create Python 3.12 virtual environment
py -3.12 -m venv carla_env

# Activate the environment
.\carla_env\Scripts\Activate.ps1

# Install CARLA Python API
pip install ..\carla\dist\carla-0.9.16-py3.7-win-amd64.egg

# Install research dependencies
pip install -r requirements.txt

# Verify installation
python -c "import carla; import cv2; import pygame; print('✅ All dependencies installed!')"
```

## Prerequisites (After Repository Setup)
- ✅ CARLA 0.9.16 simulator installed
- ✅ Python 3.12 virtual environment (`carla_env`) with CARLA Python API
- ✅ Required packages installed from `requirements.txt`
- ✅ Research scripts ready to run

## Starting CARLA

### Step 1: Start the CARLA Server

1. Open a **PowerShell** terminal (not Git Bash)
2. Navigate to CARLA root directory:
   ```powershell
   cd E:\CARLA_Latest
   ```
3. Start the CARLA server:
   ```powershell
   .\CarlaUE4.exe
   ```

**Expected Result:**
- A 3D simulator window opens showing the city environment
- The window title shows "CarlaUE4"
- You can fly around using mouse + WASD keys (this is the spectator view)
- **Keep this window open** - it's the server that your Python scripts connect to

### Step 2: Run Python Client Scripts

1. Open a **second PowerShell terminal** (keep the CARLA server running)
2. Navigate to CARLA directory and activate the environment:
   ```powershell
   cd E:\CARLA_Latest
   .\carla_env\Scripts\Activate.ps1
   ```
3. Navigate to examples folder:
   ```powershell
   cd PythonAPI\examples
   ```
4. Run your research script:
   ```powershell
   python record_driving_session.py
   ```

## Complete Workflow

### Terminal 1 (CARLA Server) - PowerShell:
```powershell
PS E:\> cd E:\CARLA_Latest
PS E:\CARLA_Latest> .\CarlaUE4.exe
# Server starts - keep this running
```

### Terminal 2 (Python Client) - PowerShell:
```powershell
PS E:\> cd E:\CARLA_Latest
PS E:\CARLA_Latest> .\carla_env\Scripts\Activate.ps1
(carla_env) PS E:\CARLA_Latest> cd PythonAPI\examples
(carla_env) PS E:\CARLA_Latest\PythonAPI\examples> python record_driving_session.py
```

## Running Other Example Scripts

Once the CARLA server is running and your environment is activated, you can run any example:

```powershell
# Manual control (like GTA-style driving)
python manual_control.py

# Generate traffic
python generate_traffic.py -n 50

# Dynamic weather
python dynamic_weather.py

# Your custom script
python simple_drive.py
```

## What You Should See

1. **CARLA Server Window**: 3D city environment (spectator view)
2. **Python Script Window**: Pygame window showing camera feed from your vehicle
3. **Console Output**: Connection status and control instructions

## Controls for simple_drive.py

- **W/A/S/D** or **Arrow Keys**: Drive the Tesla
- **TAB**: Switch between third-person and driver's view
- **SPACE**: Handbrake
- **Q**: Toggle reverse gear
- **ESC**: Quit the script

## Troubleshooting

### CARLA Server Won't Start
- Check if port 2000 is available
- Try windowed mode: `.\CarlaUE4.exe -windowed -ResX=1280 -ResY=720`
- Ensure no other CARLA instances are running

### Python Script Errors
- **"No module named carla"**: Activate the carla_env first
- **"Connection timeout"**: Make sure CARLA server is fully loaded
- **"Pygame window black"**: Script might be running but window is behind others

### Git Bash Issues
- ⚠️ **Don't use Git Bash** for running CARLA scripts
- PowerShell activation scripts (.ps1) don't work in Git Bash
- Use PowerShell for all CARLA operations

### Environment Issues
```powershell
# If activation fails, check Python version:
py -0

# Should show Python 3.12 available
# Recreate environment if needed:
py -3.12 -m venv carla_env
```

## Quick Test Sequence

1. Start CARLA server: `.\CarlaUE4.exe`
2. Wait for city to fully load
3. Open new PowerShell terminal
4. Run: `.\carla_env\Scripts\Activate.ps1`
5. Run: `cd PythonAPI\examples`
6. Run: `python simple_drive.py`
7. **Click on the pygame window** and use WASD to drive!

## For Your XAI Dataset Project

This setup is perfect for your autonomous driving dataset creation:
- **Video capture**: Camera sensors provide RGB frames
- **Action logging**: Vehicle control inputs (steering, throttle, brake)
- **Scenario creation**: Spawn other vehicles, change weather, etc.
- **Reproducible experiments**: Same scenarios, different conditions

Next steps: Modify `simple_drive.py` to add data recording capabilities for your 200-sample dataset.

## Environment Summary

- **OS**: Windows
- **CARLA Version**: 0.9.16
- **Python Version**: 3.12.7
- **Environment**: `carla_env` virtual environment
- **Required Terminal**: PowerShell (not Git Bash)
- **Server Port**: 2000 (default)
#!/usr/bin/env python3
"""
CARLA Dataset Creation - Setup Validation Script
===============================================

This script validates that your environment is properly configured for
CARLA dataset creation research. Run this after following the setup guide.

Author: XAI Autonomous Driving Research
Date: October 2025
"""

import sys
import os
import subprocess
import importlib
import json
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title):
    """Print a section header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}")

def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_warning(message):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def check_python_version():
    """Check if Python version is compatible."""
    print_section("Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Current Python version: {version_str}")
    
    if version.major == 3 and version.minor == 12:
        print_success(f"Python {version_str} is compatible with CARLA 0.9.16")
        return True
    elif version.major == 3 and version.minor >= 10:
        print_warning(f"Python {version_str} may work, but 3.12 is recommended")
        return True
    else:
        print_error(f"Python {version_str} is not compatible. Please use Python 3.12")
        return False

def check_virtual_environment():
    """Check if running in virtual environment."""
    print_section("Virtual Environment Check")
    
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        venv_path = sys.prefix
        print_success(f"Running in virtual environment: {venv_path}")
        
        # Check if it's the expected carla_env
        if 'carla_env' in venv_path:
            print_success("Using recommended 'carla_env' environment")
        else:
            print_warning("Not using 'carla_env' - ensure CARLA packages are installed")
        return True
    else:
        print_error("Not running in virtual environment!")
        print_info("Activate carla_env with: .\\carla_env\\Scripts\\Activate.ps1")
        return False

def check_required_packages():
    """Check if required Python packages are installed."""
    print_section("Python Packages Check")
    
    required_packages = {
        'carla': 'CARLA Python API',
        'pygame': 'Game development library',
        'cv2': 'OpenCV for video processing', 
        'numpy': 'Numerical computing',
        'PIL': 'Python Imaging Library'
    }
    
    all_packages_ok = True
    
    for package, description in required_packages.items():
        try:
            if package == 'cv2':
                importlib.import_module('cv2')
                import cv2
                version = cv2.__version__
            elif package == 'PIL':
                importlib.import_module('PIL')
                from PIL import Image
                version = "Available"
            else:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'Unknown')
            
            print_success(f"{description}: {version}")
        except ImportError:
            print_error(f"{description}: Not installed")
            all_packages_ok = False
    
    if not all_packages_ok:
        print_info("Install missing packages with: pip install -r requirements.txt")
    
    return all_packages_ok

def check_carla_connection():
    """Test connection to CARLA server."""
    print_section("CARLA Server Connection Check")
    
    try:
        import carla
        
        # Try to connect to CARLA
        client = carla.Client('localhost', 2000)
        client.set_timeout(5.0)  # Short timeout for testing
        
        # Test connection
        world = client.get_world()
        map_name = world.get_map().name
        
        print_success(f"Connected to CARLA server")
        print_success(f"Current map: {map_name}")
        
        # Check if world has actors (indicates server is fully loaded)
        actors = world.get_actors()
        print_info(f"Actors in world: {len(actors)}")
        
        return True
        
    except ImportError:
        print_error("CARLA package not installed")
        print_info("Install with: pip install path/to/carla/dist/carla-0.9.16-py3.7-win-amd64.egg")
        return False
    except Exception as e:
        print_error(f"Cannot connect to CARLA server: {e}")
        print_info("Make sure CARLA server is running: .\\CarlaUE4.exe")
        return False

def check_file_structure():
    """Check if required files and folders exist."""
    print_section("File Structure Check")
    
    expected_files = [
        'record_driving_session.py',
        'config.py', 
        'requirements.txt',
        'README.md',
        'CARLA_Setup_Guide.md'
    ]
    
    expected_folders = [
        'docs',
        'examples',
        'configs'
    ]
    
    all_files_ok = True
    
    # Check files
    for filename in expected_files:
        if os.path.exists(filename):
            print_success(f"Found: {filename}")
        else:
            print_error(f"Missing: {filename}")
            all_files_ok = False
    
    # Check folders
    for foldername in expected_folders:
        if os.path.exists(foldername):
            print_success(f"Found directory: {foldername}")
        else:
            print_warning(f"Missing directory: {foldername}")
    
    return all_files_ok

def check_output_folder():
    """Check if output folder exists and is writable."""
    print_section("Output Folder Check")
    
    try:
        # Import config to get output folder name
        import config
        output_folder = getattr(config, 'OUTPUT_FOLDER', 'driving_session')
    except ImportError:
        output_folder = 'driving_session'
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            print_success(f"Created output folder: {output_folder}")
        except Exception as e:
            print_error(f"Cannot create output folder: {e}")
            return False
    else:
        print_success(f"Output folder exists: {output_folder}")
    
    # Test write permissions
    test_file = os.path.join(output_folder, 'test_write.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print_success("Output folder is writable")
        return True
    except Exception as e:
        print_error(f"Cannot write to output folder: {e}")
        return False

def check_disk_space():
    """Check available disk space for recordings."""
    print_section("Disk Space Check")
    
    try:
        import shutil
        free_bytes = shutil.disk_usage('.').free
        free_gb = free_bytes / (1024**3)
        
        print_info(f"Available disk space: {free_gb:.1f} GB")
        
        if free_gb > 50:
            print_success("Sufficient disk space for dataset creation")
            return True
        elif free_gb > 10:
            print_warning("Limited disk space - plan shorter recording sessions")
            return True
        else:
            print_error("Insufficient disk space for video recording")
            print_info("Need at least 10GB free space for dataset creation")
            return False
    except Exception as e:
        print_warning(f"Cannot check disk space: {e}")
        return True

def check_config_settings():
    """Check configuration settings for research compatibility."""
    print_section("Configuration Settings Check")
    
    try:
        import config
        
        # Check key settings
        width = getattr(config, 'WINDOW_WIDTH', 1280)
        height = getattr(config, 'WINDOW_HEIGHT', 720)
        fps = getattr(config, 'FRAME_RATE', 20)
        vehicles = getattr(config, 'NUM_NPC_VEHICLES', 50)
        pedestrians = getattr(config, 'NUM_NPC_PEDESTRIANS', 30)
        
        print_info(f"Resolution: {width}x{height}")
        print_info(f"Target FPS: {fps}")
        print_info(f"NPCs: {vehicles} vehicles, {pedestrians} pedestrians")
        
        # Warn about potentially demanding settings
        if width * height > 1280 * 720:
            print_warning("High resolution - may impact performance on GTX 1650")
        
        if vehicles + pedestrians > 60:
            print_warning("High NPC count - may impact performance")
        
        if fps > 25:
            print_warning("High FPS target - may be difficult to achieve")
        
        print_success("Configuration loaded successfully")
        return True
        
    except ImportError:
        print_error("config.py not found or has errors")
        return False
    except Exception as e:
        print_error(f"Configuration error: {e}")
        return False

def run_minimal_test():
    """Run a minimal CARLA test to ensure everything works."""
    print_section("Minimal Functionality Test")
    
    try:
        import carla
        import pygame
        import numpy as np
        
        # Initialize pygame
        pygame.init()
        
        # Connect to CARLA
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        world = client.get_world()
        
        # Get a vehicle blueprint
        blueprint_library = world.get_blueprint_library()
        vehicle_bp = blueprint_library.find('vehicle.tesla.model3')
        
        # Test spawn point
        spawn_points = world.get_map().get_spawn_points()
        if spawn_points:
            print_success(f"Found {len(spawn_points)} spawn points")
        else:
            print_error("No spawn points available")
            return False
        
        print_success("Basic CARLA functionality test passed")
        return True
        
    except Exception as e:
        print_error(f"Functionality test failed: {e}")
        return False

def generate_report(results):
    """Generate a summary report."""
    print_section("Validation Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nResults: {passed}/{total} checks passed\n")
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check}")
    
    if passed == total:
        print_success(f"\n🎉 All checks passed! Your environment is ready for CARLA dataset creation.")
        print_info("You can now run: python record_driving_session.py")
    elif passed >= total - 2:
        print_warning(f"\n⚠️ Most checks passed. Review warnings above and test carefully.")
    else:
        print_error(f"\n❌ Several issues found. Please fix the problems before proceeding.")
        print_info("Refer to CARLA_Setup_Guide.md for detailed setup instructions.")

def main():
    """Main validation function."""
    print(f"{Colors.BOLD}CARLA Dataset Creation - Environment Validation{Colors.END}")
    print("This script checks if your environment is properly configured.")
    
    # Run all validation checks
    results = {
        "Python Version": check_python_version(),
        "Virtual Environment": check_virtual_environment(), 
        "Required Packages": check_required_packages(),
        "CARLA Connection": check_carla_connection(),
        "File Structure": check_file_structure(),
        "Output Folder": check_output_folder(),
        "Disk Space": check_disk_space(),
        "Configuration": check_config_settings(),
        "Basic Functionality": run_minimal_test()
    }
    
    # Generate summary report
    generate_report(results)
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Validation interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Validation script error: {e}{Colors.END}")
        sys.exit(1)
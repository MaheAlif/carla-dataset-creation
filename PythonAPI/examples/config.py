"""
CARLA Dataset Creation - Configuration Settings
===============================================

This file contains all configurable parameters for the dataset creation scripts.
Modify these settings based on your hardware capabilities and research needs.

Author: XAI Autonomous Driving Research
Date: October 2025
"""

# =============================================================================
# CARLA CONNECTION SETTINGS
# =============================================================================
CARLA_HOST = 'localhost'
CARLA_PORT = 2000
CARLA_TIMEOUT = 10.0

# =============================================================================
# VIDEO RECORDING SETTINGS
# =============================================================================
# Default settings (good for most systems)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FRAME_RATE = 20
VIDEO_CODEC = 'mp4v'  # Compatible codec for most systems

# GTX 1650 Optimized Settings (uncomment to use)
# WINDOW_WIDTH = 1024
# WINDOW_HEIGHT = 768
# FRAME_RATE = 15

# Low-end Hardware Settings (uncomment for older GPUs)
# WINDOW_WIDTH = 800
# WINDOW_HEIGHT = 600
# FRAME_RATE = 12

# =============================================================================
# NPC TRAFFIC SETTINGS
# =============================================================================
# Default settings
NUM_NPC_VEHICLES = 50
NUM_NPC_PEDESTRIANS = 30

# GTX 1650 Optimized Settings (uncomment to use)
# NUM_NPC_VEHICLES = 25
# NUM_NPC_PEDESTRIANS = 15

# Low-end Hardware Settings (uncomment for older GPUs)
# NUM_NPC_VEHICLES = 15
# NUM_NPC_PEDESTRIANS = 8

# Traffic Manager Settings
TRAFFIC_MANAGER_PORT = 8000
GLOBAL_DISTANCE_TO_LEADING_VEHICLE = 2.5  # meters
TRAFFIC_MANAGER_SYNCHRONOUS = True

# =============================================================================
# CAMERA SETTINGS
# =============================================================================
CAMERA_FOV = 110  # Field of view in degrees
CAMERA_SENSOR_TICK = 0.0  # 0.0 means as fast as possible

# Camera positions (relative to vehicle)
CAMERA_1ST_PERSON = {
    'x': 1.5,   # Forward from vehicle center
    'y': 0.0,   # Left/right offset
    'z': 2.4,   # Height above ground
    'pitch': 0.0,
    'yaw': 0.0,
    'roll': 0.0
}

CAMERA_3RD_PERSON = {
    'x': -5.5,   # Behind vehicle
    'y': 0.0,    # Left/right offset  
    'z': 2.8,    # Height above ground
    'pitch': -15.0,  # Look down slightly
    'yaw': 0.0,
    'roll': 0.0
}

# =============================================================================
# FILE OUTPUT SETTINGS
# =============================================================================
OUTPUT_FOLDER = 'driving_session'
VIDEO_FILE_PREFIX = 'recording_drive'
ACTIONS_FILE_PREFIX = 'actions_drive'
AUDIO_FILE_PREFIX = 'audio_drive'

# File formats
VIDEO_FORMAT = '.mp4'
ACTIONS_FORMAT = '.json'
AUDIO_FORMAT = '.wav'

# Audio settings (placeholder)
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 1
AUDIO_SAMPLE_WIDTH = 2

# =============================================================================
# VEHICLE SETTINGS
# =============================================================================
DEFAULT_VEHICLE_BLUEPRINT = 'vehicle.tesla.model3'
VEHICLE_SPAWN_RETRIES = 10

# Vehicle physics settings
MAX_STEER_ANGLE = 1.0      # Maximum steering input (-1.0 to 1.0)
MAX_THROTTLE = 1.0         # Maximum throttle input (0.0 to 1.0)
MAX_BRAKE = 1.0            # Maximum brake input (0.0 to 1.0)

# =============================================================================
# DATA COLLECTION SETTINGS
# =============================================================================
# Action sampling rate
ACTION_SAMPLING_RATE = 0.05  # Log actions every 50ms (20Hz)

# Minimum recording duration (seconds)
MIN_RECORDING_DURATION = 5.0

# Maximum recording duration (seconds) - prevents huge files
MAX_RECORDING_DURATION = 300.0  # 5 minutes

# =============================================================================
# RESEARCH-SPECIFIC SETTINGS
# =============================================================================
# XAI Dataset Creation Parameters
TARGET_DATASET_SIZE = 200  # Number of samples to collect
MIN_SAMPLE_DURATION = 5.0  # Minimum seconds per sample
MAX_SAMPLE_DURATION = 30.0 # Maximum seconds per sample

# Scenario diversity settings
INCLUDE_WEATHER_VARIATION = True
INCLUDE_TIME_OF_DAY_VARIATION = True
INCLUDE_TRAFFIC_DENSITY_VARIATION = True

# Action categories for XAI analysis
ACTION_CATEGORIES = [
    'IDLE',
    'ACCELERATE', 
    'BRAKE',
    'LEFT',
    'RIGHT',
    'ACCELERATE_LEFT',
    'ACCELERATE_RIGHT',
    'BRAKE_LEFT', 
    'BRAKE_RIGHT',
    'REVERSE',
    'HANDBRAKE'
]

# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================
ENABLE_PERFORMANCE_MONITORING = True
FPS_WARNING_THRESHOLD = 10  # Warn if FPS drops below this
MEMORY_WARNING_THRESHOLD_MB = 4000  # Warn if memory usage exceeds this

# Debug settings
ENABLE_DEBUG_OUTPUT = False
FRAME_COUNT_DISPLAY_INTERVAL = 20  # Show frame count every N frames

# =============================================================================
# HARDWARE-SPECIFIC PRESETS
# =============================================================================

def get_hardware_preset(preset_name):
    """Get optimized settings for specific hardware configurations."""
    
    presets = {
        'high_end': {
            'WINDOW_WIDTH': 1920,
            'WINDOW_HEIGHT': 1080,
            'FRAME_RATE': 30,
            'NUM_NPC_VEHICLES': 80,
            'NUM_NPC_PEDESTRIANS': 50,
            'CAMERA_FOV': 120
        },
        
        'gtx_1650': {
            'WINDOW_WIDTH': 1024,
            'WINDOW_HEIGHT': 768,
            'FRAME_RATE': 15,
            'NUM_NPC_VEHICLES': 25,
            'NUM_NPC_PEDESTRIANS': 15,
            'CAMERA_FOV': 90
        },
        
        'low_end': {
            'WINDOW_WIDTH': 800,
            'WINDOW_HEIGHT': 600,
            'FRAME_RATE': 12,
            'NUM_NPC_VEHICLES': 15,
            'NUM_NPC_PEDESTRIANS': 8,
            'CAMERA_FOV': 80
        }
    }
    
    return presets.get(preset_name, {})

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_config():
    """Validate configuration settings for common issues."""
    issues = []
    
    # Check resolution
    if WINDOW_WIDTH * WINDOW_HEIGHT > 1920 * 1080:
        issues.append("High resolution may cause performance issues")
    
    # Check NPC counts
    if NUM_NPC_VEHICLES + NUM_NPC_PEDESTRIANS > 100:
        issues.append("High NPC count may cause performance issues")
    
    # Check frame rate
    if FRAME_RATE > 30:
        issues.append("Frame rate above 30 may be unnecessary for dataset creation")
    
    return issues

if __name__ == "__main__":
    # Validate configuration when run directly
    issues = validate_config()
    if issues:
        print("Configuration Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration validated successfully!")
    
    # Display current settings
    print(f"\nCurrent Settings:")
    print(f"  Resolution: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    print(f"  Frame Rate: {FRAME_RATE} FPS")
    print(f"  NPCs: {NUM_NPC_VEHICLES} vehicles, {NUM_NPC_PEDESTRIANS} pedestrians")
    print(f"  Output Folder: {OUTPUT_FOLDER}")
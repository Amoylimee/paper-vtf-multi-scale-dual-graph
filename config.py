"""Configuration file for the project.

Define global constants and configuration parameters here.

Author: Amoylimee
Date: 2025-11-24
"""

from pathlib import Path

# ====================================================================
# Project Paths
# ====================================================================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# ====================================================================
# Study Area Configuration
# ====================================================================

# Main map extent: Zhoushan and Shanghai ports (WGS84)
MAIN_EXTENT = [
    121.30,  # lon_min
    123.65,  # lon_max
    29.50,   # lat_min
    31.50,   # lat_max
]

# Zhoushan study area
ZHOUSHAN_EXTENT = {
    "lon_min": 121.5056,
    "lon_max": 123.6126,
    "lat_min": 29.5607,
    "lat_max": 31.0994,
}

# Shanghai Port area
SHANGHAI_EXTENT = {
    "lon_min": 121.3500,
    "lon_max": 121.9500,
    "lat_min": 30.8500,
    "lat_max": 31.4500,
}

# ====================================================================
# Data Processing Parameters
# ====================================================================

# Trajectory subsampling: time gap in hours
TIMEGAP_HOURS = 2

# Column names
COLUMN_NAMES = {
    "id": "AIS_new",
    "time": "UTC",
    "lon": "lon",
    "lat": "lat",
}

# ====================================================================
# Parallel Processing
# ====================================================================

MAX_WORKERS = 24

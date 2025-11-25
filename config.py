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

# Map extents (WGS84)
CONTEXT_EXTENT = [117.5, 127.0, 25.5, 34.5]

ZHOUSHAN_EXTENT = [
    121.3856,  # lon_min (study_lon_min - 0.12)
    123.7326,  # lon_max (study_lon_max + 0.12)
    29.2407,   # lat_min (study_lat_min - 0.32)
    31.4194,   # lat_max (study_lat_max + 0.32)
]

SHANGHAI_EXTENT = [
    121.23,  # lon_min
    122.07,  # lon_max
    30.73,   # lat_min
    31.57,   # lat_max
]

# Area configurations (only Zhoushan/Shanghai need trajectories & grids)
AREAS = {
    "context": {
        "extent": CONTEXT_EXTENT,
        "use_tracks": False,
    },
    "zhoushan": {
        "extent": ZHOUSHAN_EXTENT,
        "use_tracks": True,
        "p1_output": OUTPUT_DIR / "p1_data_zhoushan",
        "grid_output": OUTPUT_DIR / "p2_grid_ais" / "ais_grids_zhoushan.geojson",
        "grid_resolution": 100,
    },
    "shanghai": {
        "extent": SHANGHAI_EXTENT,
        "use_tracks": True,
        "p1_output": OUTPUT_DIR / "p1_data_shanghai",
        "grid_output": OUTPUT_DIR / "p2_grid_ais" / "ais_grids_shanghai.geojson",
        "grid_resolution": 100,
    },
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

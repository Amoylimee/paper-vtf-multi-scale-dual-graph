"""Preprocess AIS trajectory data.

This script filters AIS data by geographic extent and subsamples trajectories
by keeping one random point per time window for each vessel.

Author: Amoylimee
Date: 2025-11-24
"""

from pathlib import Path
import natsort
import sinbue as sb
import iogenius as iog
import pandas as pd
import numpy as np
from helpers import set_working_directory
from config import AREAS, CONTEXT_EXTENT, COLUMN_NAMES, MAX_WORKERS


def subsample_by_timegap(
    df: pd.DataFrame, id_col: str, time_col: str, timegap_hours: float = 2
) -> pd.DataFrame:
    """
    Subsample trajectories by randomly keeping one point per time window for each trajectory.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe with trajectory data
    id_col : str
        Column name for trajectory ID
    time_col : str
        Column name for timestamp
    timegap_hours : float
        Time gap in hours for subsampling window

    Returns:
    --------
    pd.DataFrame
        Subsampled dataframe
    """
    # Ensure time column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
        df[time_col] = pd.to_datetime(df[time_col])

    # Create time bins (floor to timegap_hours intervals)
    df["_time_bin"] = df[time_col].dt.floor(f"{timegap_hours}h")

    # Group by trajectory ID and time bin, randomly sample one point per group
    sampled = df.groupby([id_col, "_time_bin"], group_keys=False).apply(
        lambda x: x.sample(n=1, random_state=42) if len(x) > 0 else x
    )

    # Drop the temporary time bin column
    sampled = sampled.drop(columns=["_time_bin"])

    return sampled.reset_index(drop=True)


def main(
    file_in: Path,
    log_dir: Path,
    context_extent: list,
    area_configs: dict,
    **kwargs,
) -> None:
    """Process a single AIS data file.

    Args:
        file_in: Input feather file path
        output_dir: Output directory path
        log_dir: Log directory path
    """
    file_in = Path(file_in)
    output_dir = Path(output_dir)
    log_dir = Path(log_dir)

    with sb.PrintRedirector(log_dir / f"{file_in.stem}.log"):
        print(f"Processing {file_in}")
        df = pd.read_feather(
            file_in, columns=[COLUMN_NAMES["id"], COLUMN_NAMES["time"], COLUMN_NAMES["lon"], COLUMN_NAMES["lat"], "speed"]
        )
        print("Input data shape:", df.shape)

        # coarse filter by context extent to cut volume once
        if context_extent:
            lon_min, lon_max, lat_min, lat_max = context_extent
            df = df[
                (df[COLUMN_NAMES["lon"]] >= lon_min)
                & (df[COLUMN_NAMES["lon"]] <= lon_max)
                & (df[COLUMN_NAMES["lat"]] >= lat_min)
                & (df[COLUMN_NAMES["lat"]] <= lat_max)
            ]
            print("After context extent filter shape:", df.shape)

        # Keep only December 2021 data
        df[COLUMN_NAMES["time"]] = pd.to_datetime(df[COLUMN_NAMES["time"]])
        df = df[df[COLUMN_NAMES["time"]].dt.month == 12]
        print("After date filter shape:", df.shape)

        # ===== No need to subsample for now ===== #
        # # Subsample: randomly keep one point per 2-hour window for each trajectory
        # df = subsample_by_timegap(
        #     df=df, id_col="AIS_new", time_col="UTC", timegap_hours=2
        # )
        # print("After sparsify shape:", df.shape)

        # per-area filtering (only areas flagged for tracks)
        for area_name, cfg in area_configs.items():
            if not cfg.get("use_tracks", False):
                continue
            lon_min, lon_max, lat_min, lat_max = cfg["extent"]
            area_df = df[
                (df[COLUMN_NAMES["lon"]] >= lon_min)
                & (df[COLUMN_NAMES["lon"]] <= lon_max)
                & (df[COLUMN_NAMES["lat"]] >= lat_min)
                & (df[COLUMN_NAMES["lat"]] <= lat_max)
            ]
            print(f"[{area_name}] after area filter shape: {area_df.shape}")

            if not area_df.empty:
                output_dir = Path(cfg["p1_output"])
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / f"{file_in.stem}.feather"
                area_df.reset_index(drop=True).to_feather(output_file)
                print(f"[{area_name}] Saved processed data to {output_file}")


if __name__ == "__main__":
    # Configure pandas display options
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", 100)

    # Set working directory
    set_working_directory()

    # Create output directories
    log_dir = Path("./logs/p1_get_data")
    iog.create_new_directory(log_dir)
    # ensure area output dirs exist
    for cfg in AREAS.values():
        if cfg.get("use_tracks") and "p1_output" in cfg:
            iog.create_new_directory(cfg["p1_output"])

    # Get input files
    input_path = Path("/disk/r102/jchenhl/Global_AIS_2021/P1_ReadData/output_P4")
    input_files = list(input_path.glob("*.feather"))
    input_files = natsort.natsorted(input_files)

    sb.process_files_parallel(
        main,
        input_files=input_files,
        log_dir=log_dir,
        context_extent=CONTEXT_EXTENT,
        area_configs=AREAS,
        max_workers=MAX_WORKERS,
        show_progress=True,
    )

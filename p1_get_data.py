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


def main(file_in: Path, output_dir: Path, log_dir: Path) -> None:
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
        df = pd.read_feather(file_in)
        print("Input data shape:", df.shape)

        # Study area extent: Zhoushan and Shanghai ports
        main_extent = [
            121.30,
            123.65,  # lon_min, lon_max
            29.50,
            31.50,  # lat_min, lat_max
        ]

        # Filter data within study extent
        df = df[
            (df["lon"] >= main_extent[0])
            & (df["lon"] <= main_extent[1])
            & (df["lat"] >= main_extent[2])
            & (df["lat"] <= main_extent[3])
        ]
        print("After extent filter shape:", df.shape)

        # Subsample: randomly keep one point per 2-hour window for each trajectory
        df = subsample_by_timegap(
            df=df, id_col="AIS_new", time_col="UTC", timegap_hours=2
        )
        print("After sparsify shape:", df.shape)

        if not df.empty:
            output_file = output_dir / f"{file_in.stem}.feather"
            df.reset_index(drop=True).to_feather(output_file)
            print(f"Saved processed data to {output_file}")


if __name__ == "__main__":
    # Configure pandas display options
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", 100)

    # Set working directory
    set_working_directory()

    # Create output directories
    output_dir = Path("./output/p1_data")
    log_dir = Path("./logs/p1_get_data")
    iog.create_new_directory(output_dir)
    iog.create_new_directory(log_dir)

    # Get input files
    input_path = Path("/disk/r102/jchenhl/Global_AIS_2021/P1_ReadData/output_P4")
    input_files = list(input_path.glob("*.feather"))
    input_files = natsort.natsorted(input_files)

    sb.process_files_parallel(
        main,
        input_files=input_files,
        output_dir=output_dir,
        log_dir=log_dir,
        max_workers=24,
        show_progress=True,
    )

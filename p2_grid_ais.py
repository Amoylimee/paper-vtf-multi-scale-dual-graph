"""Grid AIS data into spatial cells.

This script aggregates AIS point data into a regular spatial grid,
counting the number of points in each grid cell.

Author: Amoylimee
Date: 2025-11-24
"""

from pathlib import Path
import pandas as pd
import geopandas as gpd
import sinbue as sb
import iogenius as iog
from helpers import set_working_directory
from config import MAIN_EXTENT


def grid_ais_data(
    df: pd.DataFrame,
    boundary: list,
    resolution: int = 1000,
    mode: str = "count"
) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    """
    Convert point data to grid cells with statistics.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe with lon/lat columns
    boundary : list
        Boundary coordinates [lon_min, lon_max, lat_min, lat_max]
    resolution : int
        Grid cell size in meters
    mode : str
        Aggregation mode: 'count', 'sum', 'mean', etc.

    Returns:
    --------
    tuple
        (df_with_grid_ids, grids_geodataframe)
    """
    df_gridded, grids = sb.get_points_to_grids(
        data=df,
        cols=["lon", "lat"],
        boundary=boundary,
        resolution=resolution,
        mode=mode
    )
    
    print(f"Created {len(grids)} grid cells")
    print(f"Assigned {len(df_gridded)} points to grids")
    
    return df_gridded, grids


def main() -> None:
    """Main function to grid AIS data."""
    # Configure pandas display options
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", 100)

    # Set working directory
    set_working_directory()

    # Define paths
    data_dir = Path("output/p1_data")
    output_dir = Path("output/p2_grid_ais")
    iog.create_new_directory(output_dir)

    # Load all processed AIS data
    print("Loading AIS data...")
    df = iog.concat_files_in_folder(
        directory_in=data_dir,
        format="feather"
    )
    print(f"Loaded data shape: {df.shape}")

    # Grid the AIS data
    print("\nGridding AIS data...")
    df_gridded, grids = grid_ais_data(
        df=df,
        boundary=MAIN_EXTENT,
        resolution=100, 
        mode="count"
    )

    # Save grids as GeoJSON
    output_file = output_dir / "ais_grids.geojson"
    grids.to_file(output_file, driver="GeoJSON")
    print(f"\nSaved grid data to: {output_file}")


if __name__ == "__main__":
    main()
    
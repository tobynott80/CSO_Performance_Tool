import analysis
from pathlib import Path
import pandas as pd


def run_dry_day_discharge(
    run_id: int, rainfall_file: Path, spills_file: Path, heavy_rainfall: int
):
    """
    Run the dry day discharge analysis (GN066 Test 1). This function takes a long time to run so should be dispatched with a thread.

    Parameters:
    - run_id (int): The ID of the run and thread.
    - rainfall_file (Path): The path to the rainfall file.
    - spills_file (Path): The path to the spills file.
    - heavy_rainfall (int): The threshold for heavy rainfall in Mm.

    Returns:
    - None
    """
    # Create analysis logic here
    pass


def run_heavy_rainfall_discharge(
    run_id: int, rainfall_file: Path, spills_file: Path, heavy_rainfall: int
):
    """
    Run the heavy rainfall spills test (GN066 Test 2). This function takes a long time to run so should be dispatched with a thread.

    Parameters:
    - run_id (int): The ID of the run and thread.
    - rainfall_file (Path): The path to the rainfall file.
    - spills_file (Path): The path to the spills file.
    - heavy_rainfall (int): The threshold for heavy rainfall in Mm.

    Returns:
    - None

    """
    # Create analysis logic here
    pass


def run_heavy_rainfall_dry_day_discharge(
    run_id: int, rainfall_file: Path, spills_file: Path, heavy_rainfall: int
):
    """
    Run the dry day discharge analysis and heavy rainfall spills test (GN066 Test 1&2).
    GN066 tests 1&2 use much of the same logic so it makes sense to combine the two when both need to be run.
    However this function still takes a long time to run so should be dispatched with a thread.

    Parameters:
    - run_id (int): The ID of the run and thread.
    - rainfall_file (Path): The path to the rainfall file.
    - spills_file (Path): The path to the spills file.
    - heavy_rainfall (int): The threshold for heavy rainfall in Mm.

    Returns:
    - None

    """
    # Create analysis logic here
    pass

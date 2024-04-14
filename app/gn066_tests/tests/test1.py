import pandas as pd
import datetime as dt


def test_1(row, df):
    """
    Evaluates conditions for Test 1 on a given spill.
    """
    spill_start = row["Start of Spill (absolute)"]
    spill_end = row["End of Spill (absolute)"]
    prev_24hr = spill_start - dt.timedelta(hours=24)
    
    cut = df.loc[(df.index >= spill_start) & (df.index <= spill_end)]
    cut_prev_24hrs = df.loc[(df.index >= prev_24hr) & (df.index <= spill_start)]
    
    max_intensity = cut_prev_24hrs["Intensity"].max()
    max_depth_in_1hr = cut_prev_24hrs["Rolling 1hr depth"].max()
    total_depth = cut_prev_24hrs["Depth_x"].sum()
    
    if (cut["Classification"] == "Unsatisfactory").any():
        status = 'Fail'
    else:
        status = 'Pass'
    
    return max_intensity, max_depth_in_1hr, total_depth, status
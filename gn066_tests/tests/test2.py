import pandas as pd

def test_2(row, df, results_ts):
    """
    Evaluates conditions for Test 2 on a given spill.
    """
    spill_start = pd.to_datetime(row["Start of Spill (absolute)"]).round(results_ts)
    
    try:
        if (df.loc[df.index == spill_start, "Classification"] == "Satisfactory").bool():
            return 'Pass'
        else:
            return 'Fail'
    except ValueError:  # Adjusted to catch specific exceptions
        return 'idk'
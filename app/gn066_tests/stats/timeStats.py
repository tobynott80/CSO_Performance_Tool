import pandas as pd
import app.gn066_tests.config as c
import datetime as dt

def time_stats (df, spills_baseline):
    """
    Function that pulls out key data about % of the year
    """
    years = []
    dry_perc = []
    heavy_perc = []
    spill_perc = [[] for _ in range(1)]
    for yr,yr_grp in df.groupby(pd.Grouper(freq='Y')):
        years.append(yr.year)
        dry_perc.append(yr_grp["Classification"].value_counts()['Unsatisfactory'] / len(yr_grp) * 100)
        heavy_perc.append(yr_grp["Classification"].value_counts()['Satisfactory'] / len(yr_grp) * 100)
        run_name = spills_baseline[2]
        try:
            spill_perc[0].append(yr_grp[run_name].value_counts()['YES'] / len(yr_grp) * 100)
        except:
            spill_perc[0].append(0)


    years.append("Whole Time Series")
    dry_perc.append(df["Classification"].value_counts()['Unsatisfactory'] / len(df) * 100)
    heavy_perc.append(df["Classification"].value_counts()['Satisfactory'] / len(df) * 100)
    run_name = spills_baseline[2]
    spill_perc[0].append(df[run_name].value_counts()['YES'] / len(df) * 100)

    annual_summary = pd.DataFrame({"Year": years, "Percentage of dry days (%)": dry_perc, "Percentage of year spills are allowed to start (%)": heavy_perc})
    run_name = spills_baseline[2]
    annual_summary [run_name+" - Percentage of year spilling (%)"] = spill_perc[0]

    return(annual_summary)


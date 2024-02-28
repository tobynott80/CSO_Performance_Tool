import pandas as pd
import config as c
import datetime as dt

def time_stats (df):
    """
    Function that pulls out key data about % of the year
    """
    years = []
    dry_perc = []
    heavy_perc = []
    spill_perc = [[] for _ in range(len(c.runs))]
    for yr,yr_grp in df.groupby(pd.Grouper(freq='Y')):
        years.append(yr.year)
        dry_perc.append(yr_grp["Classification"].value_counts()['Unsatisfactory'] / len(yr_grp) * 100)
        heavy_perc.append(yr_grp["Classification"].value_counts()['Satisfactory'] / len(yr_grp) * 100)
        for i, run in enumerate(c.runs):
            run_name = run[2]
            try:
                spill_perc[i].append(yr_grp[run_name].value_counts()['YES'] / len(yr_grp) * 100)
            except:
                spill_perc[i].append(0)


    years.append("Whole Time Series")
    dry_perc.append(df["Classification"].value_counts()['Unsatisfactory'] / len(df) * 100)
    heavy_perc.append(df["Classification"].value_counts()['Satisfactory'] / len(df) * 100)
    for i, run in enumerate(c.runs):
        run_name = run[2]
        spill_perc[i].append(df[run_name].value_counts()['YES'] / len(df) * 100)

    annual_summary = pd.DataFrame({"Year": years, "Percentage of dry days (%)": dry_perc, "Percentage of year spills are allowed to start (%)": heavy_perc})
    for i, run in enumerate(c.runs):
        run_name = run[2]
        annual_summary [run_name+" - Percentage of year spilling (%)"] = spill_perc[i]

    return(annual_summary)


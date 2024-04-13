# This will contain sewage_be_spilling data

import pandas as pd
import app.gn066_tests.config as config


def sewage_be_spillin(spills_baseline, df, heavy_rain):
    """ 
    Read in spills from either an Excel sheet or CSV stats template output and define start and end of spill event. Compare to rainfall dataframe and add 'run_spill?' column to be filled with yes if 
    rainfall dataframe index falls in a spill event period
    """

    def day_type(row):
        if row["Depth"] > 0.25:
            return "Wet"
        elif row["prev_day"] > 0.25:
            return "Previous Day Wet"
        else:
            return "Dry"

    def classification_by_time(row):
        if row["Day Type"] == "Dry":
            return "Unsatisfactory"
        elif row["Spill_allowed?"] == "YES":
            return "Satisfactory"
        else:
            return "Substandard"

    # Resample rainfall data by calendar day and add a column with the shifeted data to represent previous day
    daily_rainfall = pd.DataFrame(df["Depth"].resample('1D').sum())
    daily_rainfall['prev_day'] = daily_rainfall.shift(1).fillna(0)
    # Classify the day type
    daily_rainfall["Day Type"] = daily_rainfall.apply(
        lambda row: day_type(row), axis=1)
    print(daily_rainfall.head(10))

    df = df.assign(key=df.index.normalize())
    df = df.merge(daily_rainfall, left_on='key', right_index=True, how='left')
    df.drop(['key', 'Depth_y', 'prev_day'], axis=1, inplace=True)

    df["Spill_allowed?"] = None
    # If intersity in last 24hours is greater than heavy rainfall definition then fill column with yes
    rolling_max = df['Rolling 1hr depth'].rolling('24H').max()
    df.loc[rolling_max >= config.heavy_rain, 'Spill_allowed?'] = 'YES'
    # print (df.head(10))

    df["Classification"] = df.apply(
        lambda row: classification_by_time(row), axis=1)

    spills_df = pd.DataFrame()

    # Read in spills from either an Excel sheet or CSV stats template output
    run_name = spills_baseline[2]
    print(run_name)
    # Add a column for the run in the rainfall database
    df[run_name] = None
    # Read the stats report
    spills = spills_baseline[0]
    # if spill_counts.filename.rsplit('.', 1)[-1] == "xlsx":
    #     spills = pd.read_excel(spill_counts)
        
    # else:
    #     spills = pd.read_csv(spill_counts)
    print(spills.columns)
    # Define the start and end as datetime format
    spills["Start of Spill (absolute)"] = pd.to_datetime(
        spills["Start of Spill (absolute)"], format="%Y-%m-%d %H:%M:%S")
    spills["End of Spill (absolute)"] = pd.to_datetime(
        spills["End of Spill (absolute)"], format="%Y-%m-%d %H:%M:%S")
    spills["RUN"] = run_name
    spills_df = pd.concat([spills_df, spills], ignore_index=True)
    # If index is time during spill event for run, add YES in that column
    for spill_start, spill_end in spills[['Start of Spill (absolute)', 'End of Spill (absolute)']].itertuples(index=False):
        df.loc[(df.index >= spill_start) & (
            df.index <= spill_end), run_name] = "YES"
    print(spills_df.head(10))
    print(df.head(10))

    # Save stuff
    # df.to_excel(outfolder/"GN066 analyses.xlsx", sheet_name = 'Time series dataframe') # This could fail if saving full 10 years at 5min ts, may need to put in a check on df length and cut if too long before saving to excel (just for saving only, analysis still done on all of it)
    # daily_rainfall.to_excel(outfolder/"Rainfall Analysis Wet Dry Days.xlsx")

    return (df, spills_df)

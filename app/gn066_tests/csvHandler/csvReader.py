import pandas as pd
import datetime as dt
intensity = True

def init(rainfall_file):
    df_rain = pd.read_csv(rainfall_file,skiprows=13)
    df_rain["P_DATETIME"] = pd.to_datetime(df_rain["P_DATETIME"],format="%d/%m/%Y %H:%M:%S")
    df_rain_dtindex = df_rain.set_index("P_DATETIME",drop=False)
    return df_rain_dtindex

def aggregate_rainfall_directly(df_rain):

    yearly_totals = df_rain.resample('YE').sum()["Intensity"]
    summary_df = pd.DataFrame(yearly_totals).reset_index()
    summary_df.columns = ['Year', 'Total Rainfall (mm)']
    summary_df['Year'] = summary_df['Year'].dt.year
    
    # Now print the dataframe as a string and concatenate your test message
    print(summary_df.to_string(index=False))
    return summary_df

def readCSV(df_rain_dtindex):
    ### Reformat rolling rainfall data ###

    if intensity:
        df_rain_dtindex["ts"] = df_rain_dtindex.index.to_series().diff().fillna(method='bfill')
        df_rain_dtindex["multiplier"] = df_rain_dtindex["ts"].apply(lambda ts: ts/dt.timedelta(hours=1))
        df_rain_dtindex["Depth"] = df_rain_dtindex["1"] * df_rain_dtindex["multiplier"]
        df_rain_dtindex["Intensity"] = df_rain_dtindex["1"]
        # Drop useless columsn for clarity's sake
        df_rain_dtindex.drop(['ts', 'multiplier', '1' ,"P_DATETIME"], axis=1, inplace=True)

    else:
        df_rain_dtindex["Depth"] = df_rain_dtindex["1"]
        df_rain_dtindex["ts"] = df_rain_dtindex.index.to_series().diff().fillna(method='bfill')
        df_rain_dtindex["multiplier"] = df_rain_dtindex["ts"].apply(lambda ts: dt.timedelta(hours=1)/ts)
        df_rain_dtindex["Intensity"] = df_rain_dtindex["Depth"] * df_rain_dtindex["multiplier"]
        df_rain_dtindex.drop(['ts', 'multiplier','1' ,"P_DATETIME"], axis=1, inplace=True)

    df_rain_dtindex["Rolling 1hr depth"] = df_rain_dtindex["Depth"].rolling('1h').sum()

    print (df_rain_dtindex.head(10))



    # For faster runs
    #start_date = dt.datetime(2019,1,1,0,0,0)
    #end_date = dt.datetime(2022,1,1,0,0,0)
    #df_rain_dtindex = df_rain_dtindex.loc[(df_rain_dtindex.index >= start_date) & (df_rain_dtindex.index <= end_date)]

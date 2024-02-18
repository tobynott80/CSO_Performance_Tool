#!/usr/bin/env python
"""
Created on Mon Dec 12 2023

@author: Amelie

GN066 Processing to produce a workbook with summary stats, full timeseries database, and spill database. It also produces a visual for time period of choice.
User can choose to add as many model runs as they want to process in the same worksheet/visual. It is recommended to limit to 3 short-list options

"""
# coding: utf-8

# In[1]:

import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from pathlib import Path
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection



# In[3]:

### Set inputs ###

#Link to rainfall data. Currently takes data extracted from ICM 
rainfall_file = Path(r"\\global\europe\Cardiff\Jobs\275000\275214-00\4 Internal Project Data\4-20 Studies\33110 Mill Street Castle Meadows\3. Options\Storage Volume\GN066 - exploration\Inputs\SOAF_NRW_Rainfall 2012-2023.csv")

# Definition of head rain (depth recorded in an hour)
heavy_rain = 4

#Define where spill stats reports are saved for all runs. This should be a copy of the ICM spill template. Format is file path, sheet name, option short description
# In the future can just make this read files in a folder if wanted
runs =[]
spills_baseline = (Path(r"\\global\europe\Cardiff\Jobs\275000\275214-00\4 Internal Project Data\4-20 Studies\33110 Mill Street Castle Meadows\3. Options\Storage Volume\GN066 - exploration\Inputs\OCBL - stats report.xlsx"), "None", "OC Fixed Baseline")
#spills_opt_1 = (Path(r"C:\Users\Amelie.Loubens\OneDrive - Arup\Desktop\GN066 exploration\Sites\Trelewis\Trelewis_Catchment_Spill_Analysis_IDP4 Base&Solution.xlsx"), "Scenario_20", "Preffered solution")
#spills_opt_2 = (Path(r"C:\Users\Amelie.Loubens\OneDrive - Arup\Desktop\GN066 exploration\Sites\Hirwaun\2023-12-21_BEC_STRS_H_ReducedRS No LambRd Offline Storage 1E50223 Rainfall intensity.xlsx"), "Exceedance detail", "Offline storage")
#spills_opt_3 = (Path(r"C:\Users\Amelie.Loubens\OneDrive - Arup\Desktop\GN066 exploration\stats templates\Strand solutions.xlsx"), "V4 storage + 2.75ha RS", "Option 3 - 400m3 storage + 2.75ha RS")
runs.append(spills_baseline)
results_ts = '15T' # Can automate this
# Add more if required


# In[4]:

### Set where you want outputs ###

#Define where analysis is being saved
outfolder = Path(r"\\global\europe\Cardiff\Jobs\275000\275214-00\4 Internal Project Data\4-20 Studies\33110 Mill Street Castle Meadows\3. Options\Storage Volume\GN066 - exploration")
outfolder.mkdir(exist_ok=True)


# In[5]:


#Set to True if data is intensity, False if depth is measured
#Assume intensity is mm/hr
intensity = True


# In[6]:

### Read in Rainfall ###

df_rain = pd.read_csv(rainfall_file,skiprows=13)
df_rain["P_DATETIME"] = pd.to_datetime(df_rain["P_DATETIME"],format="%d/%m/%Y %H:%M:%S")
df_rain_dtindex = df_rain.set_index("P_DATETIME",drop=False)
print (df_rain_dtindex.head(10))


# In[7]:

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


# In[12]:

### Classify Year in Periods where spills are Satisfactory/Substandard/Unsatisfactory

def sewage_be_spillin(runs, df, heavy_rain):
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
        
    def classification_by_time (row):
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
    daily_rainfall["Day Type"] = daily_rainfall.apply(lambda row: day_type(row),axis=1)
    print (daily_rainfall.head(10))
    

    df = df.assign(key=df.index.normalize())
    df = df.merge(daily_rainfall, left_on='key', right_index=True, how='left')
    df.drop(['key', 'Depth_y', 'prev_day'], axis=1, inplace=True)

    df["Spill_allowed?"] = None
    # If intersity in last 24hours is greater than heavy rainfall definition then fill column with yes
    rolling_max = df['Rolling 1hr depth'].rolling('24H').max()
    df.loc[rolling_max >= heavy_rain, 'Spill_allowed?'] = 'YES'
    # print (df.head(10))

    df["Classification"] = df.apply(lambda row: classification_by_time(row),axis=1)

    spills_df = pd.DataFrame()

    for run in runs:
        #Read in spills from either an Excel sheet or CSV stats template output
        run_name = run[2]
        print(run_name)
        # Add a column for the run in the rainfall database
        df[run_name] = None

        # Read the stats report
        spill_counts = run [0]
        sheet_name = run[1]
        if spill_counts.suffix == ".xlsx":
            sheets = pd.read_excel(spill_counts,sheet_name = None)
            if len(sheets)>1:
                sheet_name = sheet_name
                spills = pd.read_excel(spill_counts,sheet_name=sheet_name)
            else:
                spills = pd.read_excel(spill_counts)
        else:
            spills = pd.read_csv(spill_counts)

        #Define the start and end as datetime format
        spills["Start of Spill (absolute)"] = pd.to_datetime(spills["Start of Spill (absolute)"],format="%Y-%m-%d %H:%M:%S")
        spills["End of Spill (absolute)"] = pd.to_datetime(spills["End of Spill (absolute)"],format="%Y-%m-%d %H:%M:%S")

        spills ["RUN"] = run_name

        spills_df = pd.concat([spills_df,spills], ignore_index =True)

        # If index is time during spill event for run, add YES in that column
        for spill_start, spill_end in spills[['Start of Spill (absolute)', 'End of Spill (absolute)']].itertuples(index=False):
            df.loc[(df.index >= spill_start.round(results_ts)) & (df.index <= spill_end.round(results_ts)), run_name] = "YES"


    print (spills_df.head(10))
    print (df.head(10))

    # Save stuff
    #df.to_excel(outfolder/"GN066 analyses.xlsx", sheet_name = 'Time series dataframe') # This could fail if saving full 10 years at 5min ts, may need to put in a check on df length and cut if too long before saving to excel (just for saving only, analysis still done on all of it)
    #daily_rainfall.to_excel(outfolder/"Rainfall Analysis Wet Dry Days.xlsx")

    return (df, spills_df)

# In[]
df, spills_df = sewage_be_spillin(runs, df_rain_dtindex, heavy_rain)        

# In[13]:

###### Run cell for timeline visual ######

# Define the period you want to display for the timeline. Math is done for all 10 years
timeline_start = dt.datetime(2020,1,1,0,0,0)
timeline_end = dt.datetime(2020,12,31,0,0,0)

def timeline_visual (runs, df, timeline_start, timeline_end):
    """
    Make a pretty time line graph from defined start to finish
    """

    data = df.loc[(df.index >= timeline_start) & (df.index <= timeline_end)]

    # Creating empty lists to store start and end dates for collection of bars
    test_1_bars = []
    test_2_bars = []
    combined_bars = []
    spill_bars = []
    for i in range(1,len(data)):
        # Test 2
        if data.iloc[i]['Spill_allowed?'] == 'YES' and (data.iloc[i-1]['Spill_allowed?']!= 'YES' or i==1):
            #print (i)
            start_date = data.index[i]
            #print (start_date)
            for j in range(i+1, len(data)):
                if data.iloc[j]['Spill_allowed?'] != 'YES':
                    #print (j)
                    end_date = data.index[j]
                    test_2_bars.append((start_date, end_date, 'Test 2 Pass'))
                    combined_bars.append((start_date, end_date, 'Satisfactory'))
                    break
                if j == (len(data)-1):
                    end_date = data.index[j]
                    test_2_bars.append((start_date, end_date, 'Test 2 Pass'))
                    combined_bars.append((start_date, end_date, 'Satisfactory'))
                    break
        elif data.iloc[i]['Spill_allowed?'] != 'YES' and (data.iloc[i-1]['Spill_allowed?'] == 'YES' or i==1):
            #print (i)
            start_date = data.index[i]
            #print (start_date)
            for j in range(i+1, len(data)):
                if data.iloc[j]['Spill_allowed?'] == 'YES':
                    #print (j)
                    end_date = data.index[j]
                    test_2_bars.append((start_date, end_date, 'Test 2 Fail'))
                    combined_bars.append((start_date, end_date, 'Substandard'))
                    break
                if j == (len(data)-1):
                    end_date = data.index[j]
                    test_2_bars.append((start_date, end_date, 'Test 2 Fail'))
                    combined_bars.append((start_date, end_date, 'Substandard'))
                    break

    for i in range(1,len(data)):               
        # Test 1
        if data.iloc[i]['Day Type'] == 'Dry'and (data.iloc[i-1]['Day Type']!= 'Dry'or i==1):
            start_date = data.index[i]
            for j in range(i+1, len(data)):
                if data.iloc[j]['Day Type'] != 'Dry':
                    end_date = data.index[j]
                    test_1_bars.append((start_date, end_date, 'Test 1 Fail'))
                    combined_bars.append((start_date, end_date, 'Unsatisfactory'))
                    break
                if j == (len(data)-1):
                    end_date = data.index[j]
                    test_1_bars.append((start_date, end_date, 'Test 1 Fail'))
                    combined_bars.append((start_date, end_date, 'Unsatisfactory'))
                    break
        if data.iloc[i]['Day Type'] != 'Dry'and (data.iloc[i-1]['Day Type']== 'Dry'or i==1):
            start_date = data.index[i]
            for j in range(i+1, len(data)):
                if data.iloc[j]['Day Type'] == 'Dry':
                    end_date = data.index[j]
                    test_1_bars.append((start_date, end_date, 'Test 1 Pass'))
                    break
                if j == (len(data)-1):
                    end_date = data.index[j]
                    test_1_bars.append((start_date, end_date, 'Test 1 Pass'))
                    break


    for i in range(1,len(data)):
        # Spills data
        for run in runs:
            run_name = run[2]
            if data.iloc[i][run_name] == 'YES'and data.iloc[i-1][run_name]!= 'YES':
                start_date = data.index[i]
                for j in range(i+1, len(df)):
                    if data.iloc[j][run_name] != 'YES':
                        end_date = data.index[j]
                        spill_bars.append((start_date, end_date, run_name))
                        
                        break

    print (test_1_bars)
    print (test_2_bars)
    print (spill_bars)
    bars = test_2_bars + test_1_bars + combined_bars + spill_bars 

    # On to graphing
    cycle = ['white', 'forestgreen', 'firebrick', 'darkorange', 'purple','navy','blue', 'dodgerblue', 'deepskyblue', 'lightskyblue', ' paleturquoise']
    cats = {"Test 1 Pass" : 1, "Test 1 Fail" : 1, "Test 2 Pass" : 2, "Test 2 Fail" : 2, "Satisfactory" : 3, "Substandard" : 3, "Unsatisfactory" : 3}
    colormapping = {"Test 1 Pass" : cycle[0], "Test 1 Fail" : cycle[0], "Test 2 Pass" : cycle[0], "Test 2 Fail" : cycle[0], "Satisfactory" : cycle[1], "Substandard" : cycle[3], "Unsatisfactory" : cycle[2]}
    y_labels = ["", "", "Classification"]
    for i in range(len(runs)):
        cats.update({runs[i][2] : i + 4})
        colormapping.update({runs[i][2] : cycle[i+4]})
        y_labels.append(runs[i][2])

    print (cats)
    print (colormapping)
    print (y_labels)

    verts = []
    colors = []
    for bar in bars:
        v =  [(mdates.date2num(bar[0]), cats[bar[2]]-.49),
            (mdates.date2num(bar[0]), cats[bar[2]]+.49),
            (mdates.date2num(bar[1]), cats[bar[2]]+.49),
            (mdates.date2num(bar[1]), cats[bar[2]]-.49),
            (mdates.date2num(bar[0]), cats[bar[2]]-.49)]
        verts.append(v)
        colors.append(colormapping[bar[2]])

    library = PolyCollection(verts, facecolors=colors)
    # Create figure
    fig, ax = plt.subplots(figsize=(60, len(runs)*2))
    ax.add_collection(library)
    ax.autoscale()
    if timeline_end - timeline_start <= dt.timedelta(30,0):
        loc = mdates.DayLocator(interval=1)
    elif timeline_end - timeline_start <= dt.timedelta(60,0):
        loc = mdates.DayLocator(bymonthday=[0,7,14,21,28])
    else:
        loc = mdates.DayLocator(bymonthday=[0,15,30])
    days = mdates.DayLocator(interval=1)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_minor_locator(days)
    ax.grid(which='minor', color='#F0F0F0', linewidth=0.5, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(loc))

    ax.set_yticks([i for i in range(1, len(runs) + 4)])
    ax.set_yticklabels(y_labels)
    ax.grid(which='major', axis='x')

    # Add rainfall depth
    ax2 = ax.twinx()
    ax2.plot(data.index, data['Rolling 1hr depth'], 'b-' )
    ax2.plot(data.index, np.full(len(data),heavy_rain), 'k--')
    ax2.set_ylabel('Rainfall depth over any hour (mm)')
    ax2.set_ylim(0, data['Rolling 1hr depth'].max()*(len(runs)+3)/3)
    
    plt.show()
    

timeline_visual(runs, df, timeline_start, timeline_end)

# In[14]:

### Run for Percentage Stats ###

def time_stats (df):
    """
    Function that pulls out key data about % of the year
    """
    years = []
    dry_perc = []
    heavy_perc = []
    spill_perc = [[] for _ in range(len(runs))]
    for yr,yr_grp in df.groupby(pd.Grouper(freq='Y')):
        years.append(yr.year)
        dry_perc.append(yr_grp["Classification"].value_counts()['Unsatisfactory'] / len(yr_grp) * 100)
        heavy_perc.append(yr_grp["Classification"].value_counts()['Satisfactory'] / len(yr_grp) * 100)
        for i, run in enumerate(runs):
            run_name = run[2]
            try:
                spill_perc[i].append(yr_grp[run_name].value_counts()['YES'] / len(yr_grp) * 100)
            except:
                spill_perc[i].append(0)


    years.append("Whole Time Series")
    dry_perc.append(df["Classification"].value_counts()['Unsatisfactory'] / len(df) * 100)
    heavy_perc.append(df["Classification"].value_counts()['Satisfactory'] / len(df) * 100)
    for i, run in enumerate(runs):
        run_name = run[2]
        spill_perc[i].append(df[run_name].value_counts()['YES'] / len(df) * 100)

    annual_summary = pd.DataFrame({"Year": years, "Percentage of dry days (%)": dry_perc, "Percentage of year spills are allowed to start (%)": heavy_perc})
    for i, run in enumerate(runs):
        run_name = run[2]
        annual_summary [run_name+" - Percentage of year spilling (%)"] = spill_perc[i]

    return(annual_summary)


perc_data = time_stats(df)
print (perc_data)

# In[]

### Run for Spill Count Stats ###

def spill_stats (spills_df,df):
    """
    Count satisfactory/substandard/unsatisfactory following the GN066 Test 1/2 criteria interpreted in a different way
    """
    
    #Create a dataframe just with the spill start and volume
    spills_df = spills_df[["Sim","ID","Start of Spill (absolute)","End of Spill (absolute)","Spill Volume (m3)", "RUN"]]

    def test_1 (row):
        # If any point of the spill is on a dry day, then unsatisfactory
        spill_start = row["Start of Spill (absolute)"]
        spill_end = row["End of Spill (absolute)"]
        prev_24hr = row["Start of Spill (absolute)"] - dt.timedelta(hours = 24)

        cut = df.loc[(df.index >= spill_start) & (df.index <= spill_end)]
        cut_prev_24hrs = df.loc[(df.index >= prev_24hr) & (df.index <= spill_start)]
        # Collect this useful stuff during this test too
        max_intensity = cut_prev_24hrs["Intensity"].max()
        max_depth_in_1hr = cut_prev_24hrs["Rolling 1hr depth"].max()
        total_depth = cut_prev_24hrs["Depth_x"].sum()
        
        if (cut["Classification"] == "Unsatisfactory").any():
            return max_intensity, max_depth_in_1hr, total_depth, 'Fail'
        else:
            return max_intensity, max_depth_in_1hr, total_depth, 'Pass'
        
        
    def test_2_depth_start (row):
        # If start of spill falls in the satisfactory then satisfactory
        spill_start = row["Start of Spill (absolute)"].round(results_ts) #round to nearest timestep to get a value
        #print(spill_start, df.loc[df.index == spill_start, "Classification"] == "Satisfactory")
        try:
            if (df.loc[df.index == spill_start, "Classification"] == "Satisfactory").bool():
                return 'Pass'
            else:
                return 'Fail'
        except:
            return 'idk'
    

    print ('Starting to run test 1')
    # RUN TEST 1
    spills_df [['Max intensity in 24hrs preceding spill start (mm/hr)', 'Max depth in an hour in 24hrs preceding spill start (mm/hr)', ' Total depth in 24hrs preceding spill start (mm)', 'Test 1']] = spills_df.apply(test_1, axis = 1, result_type ='expand')
    print ('Done Test 1')

    # RUN TEST 2
    spills_df ['Test 2'] = spills_df.apply(test_2_depth_start, axis = 1)
    print ('Done Test 2')

    # FInal Classification
    def spill_class (row):
        if row["Test 1"] == "Fail":
            return "Unsatisfactory"
        elif row["Test 2"] == "Pass":
            return "Satisfactory"
        else:
            return "Substandard"
        
    print ('Starting Count')

    # Count Spills
    spills_df ['Classification'] = spills_df.apply(spill_class, axis = 1)
        
    years = []
    spill_count = [[] for _ in range(len(runs)*3)]

    for yr,yr_grp in spills_df.groupby(pd.Grouper(key="Start of Spill (absolute)", freq='Y')):
        print (yr.year)
        years.append(yr.year)
        for i, (run, run_grp) in enumerate(yr_grp.groupby(['RUN'])):
            spill_count[i*3].append(run_grp['Classification'].value_counts().get('Unsatisfactory',0))
            spill_count[(i*3) + 1].append(run_grp['Classification'].value_counts().get('Substandard',0))
            spill_count[(i*3) + 2].append(run_grp['Classification'].value_counts().get('Satisfactory',0))

    years.append("Whole Time Series")
    run_names =[]
    for i, (run, run_grp) in enumerate(spills_df.groupby(['RUN'])):
        run_names.append(run[0])
        spill_count[i*3].append(run_grp['Classification'].value_counts().get('Unsatisfactory',0))
        spill_count[(i*3) + 1].append(run_grp['Classification'].value_counts().get('Substandard',0))
        spill_count[(i*3) + 2].append(run_grp['Classification'].value_counts().get('Satisfactory',0))
    #print (spill_count)

    annual_summary = pd.DataFrame({"Year": years})
    for i, run_name in enumerate(run_names):
        annual_summary [run_name+" - Unsatisfactory Spills"] = spill_count[i*3]
        annual_summary [run_name+" - Substandard Spills"] = spill_count[(i*3) + 1]    
        annual_summary [run_name+" - Satisfactory Spills"] = spill_count[(i*3) + 2]    

    return interpretation_name, spills_df, annual_summary

interpretation_name, all_spill_classification, spill_count_data = spill_stats(spills_df, df)

# In[]
# Combine perc and count stats and add an interpretation name heading
summary = pd.merge(perc_data, spill_count_data, on = 'Year')
print (summary)

### Save Stats and Spills database to same excel workbook - can take 5min
writer = pd.ExcelWriter(outfolder/"GN066 analyses - Castle Meadows.xlsx", engine='xlsxwriter')
summary.to_excel(writer, sheet_name = 'Summary', startrow=1, index= False)
worksheet = writer.sheets['Summary']
worksheet.write(0, 0, interpretation_name)
try:
    df.to_excel(writer, sheet_name = 'Time series dataframe')
except: # If too long too save
    start_date = dt.datetime(2013,1,1,0,0,0)
    end_date = dt.datetime(2023,1,1,0,0,0)
    df = df.loc[(df.index >= start_date) & (df.index <= end_date)]
    df.to_excel(writer, sheet_name = 'Time series dataframe', startrow=1)
    worksheet = writer.sheets['Time series dataframe']
    worksheet.write(0, 0, '2013-2022 only due to length')

all_spill_classification.to_excel(writer, sheet_name = 'Spills dataframe')

writer.close()
# %%

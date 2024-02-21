#!/usr/bin/env python
#utf-8

#imports
import csvHandler.csvReader as csvReader
import csvHandler.csvWriter as csvWriter
import stats.timeStats as ts
import stats.spillStats as ss
import visualisation as vis
import analysis as analysis
import config as config
import pandas as pd
import datetime as dt
pd.options.mode.chained_assignment = None  # default='warn'

#config
rainfall_file = config.rainfall_file
heavy_rain = config.heavy_rain
spills_baseline = config.runs
runs = config.runs
spills_baseline = config.spills_baseline
outfolder = config.outfolder
exists = config.exists
runs.append(spills_baseline)

#Read csv and reformats
df_rain_dtindex = csvReader.init()
csvReader.readCSV(df_rain_dtindex)

#Performs sewage be spilling malarky
df, spills_df = analysis.sewage_be_spillin(runs, df_rain_dtindex, heavy_rain)

#Creates visualisation
vis.timeline_visual(runs, df, vis.timeline_start, vis.timeline_end)

#Creates time stats and spill stats
perc_data = ts.time_stats(df)
# print (perc_data)

# To run only Test 1:
all_spill_classification, spill_count_data = ss.spill_stats(spills_df, df, [1])

# Or, to run only Test 2:
# all_spill_classification, spill_count_data = ss.spill_stats(spills_df, df, [2])

# Or, to run both Test 1 and Test 2:
# all_spill_classification, spill_count_data = ss.spill_stats(spills_df, df, [1, 2])


# Combine perc and count stats and add an interpretation name heading
summary = pd.merge(perc_data, spill_count_data, on = 'Year')
print (summary)

# Write to file
csvWriter.writeCSV(df, summary, all_spill_classification)

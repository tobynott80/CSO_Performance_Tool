import pandas as pd
import config as c
import datetime as dt
import main as main 


### Save Stats and Spills database to same excel workbook - can take 5min
writer = pd.ExcelWriter(c.outfolder/"GN066 analyses - Castle Meadows.xlsx", engine='xlsxwriter')
main.summary.to_excel(writer, sheet_name = 'Summary', startrow=1, index= False)
worksheet = writer.sheets['Summary']
# worksheet.write(0, 0)
try:
    main.df.to_excel(writer, sheet_name = 'Time series dataframe')
except: # If too long too save
    start_date = dt.datetime(2013,1,1,0,0,0)
    end_date = dt.datetime(2023,1,1,0,0,0)
    df = main.df.loc[(main.df.index >= start_date) & (main.df.index <= end_date)]
    df.to_excel(writer, sheet_name = 'Time series dataframe', startrow=1)
    worksheet = writer.sheets['Time series dataframe']
    worksheet.write(0, 0, '2013-2022 only due to length')

main.all_spill_classification.to_excel(writer, sheet_name = 'Spills dataframe')

writer.close()
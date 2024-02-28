from pathlib import Path

# Set inputs
# e.g Dry day and heavy rainfall discharges (Test1&2)/Examples/Castle Meadows/Inputs/SOAF_NRW_Rainfall 2012-2023.csv
rainfall_file = Path(r"./Castle Meadows/Inputs/SOAF_NRW_Rainfall 2012-2023.csv")

#Define where spill stats reports are saved for all runs. This should be a copy of the ICM spill template. Format is file path, sheet name, option short description
# In the future can just make this read files in a folder if wanted
#For castle meadows its the OCBL - stats report.xlsx file you need the location of:
runs =[]
spills_baseline = (Path(r"./Castle Meadows/Inputs/OCBL - stats report.xlsx"), "None", "OC Fixed Baseline")

# Define where outputs should be saved 
outfolder = Path("")
exists = outfolder.mkdir(exist_ok=True)

# Definition of heavy rain (depth recorded in an hour)
heavy_rain = 4  
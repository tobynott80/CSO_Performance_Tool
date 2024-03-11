import pandas as pd
import app.gn066_tests.config as c
import datetime as dt
results_ts = '15T'
import app.gn066_tests.tests.test1 as test1
import app.gn066_tests.tests.test2 as test2

test1
test2

def spill_stats(spills_df, df, run_tests=[1, 2]):
    """
    Applies Test 1 and/or Test 2 to classify spills and summarizes the results.
    
    Parameters:
    - spills_df: DataFrame containing spill data.
    - df: DataFrame containing environmental data used by the tests.
    - run_tests: List specifying which tests to run. Default is [1, 2] to run both tests.
    """
    # Filter to relevant columns
    spills_df = spills_df[["Sim", "ID", "Start of Spill (absolute)", "End of Spill (absolute)", "Spill Volume (m3)", "RUN"]]
    
    if 1 in run_tests:
        # Apply Test 1
        print('Starting to run Test 1')
        test_1_results = spills_df.apply(lambda row: test1.test_1(row, df), axis=1, result_type='expand')
        spills_df[['Max intensity in 24hrs preceding spill start (mm/hr)', 
                   'Max depth in an hour in 24hrs preceding spill start (mm/hr)', 
                   'Total depth in 24hrs preceding spill start (mm)', 
                   'Test 1 Status']] = test_1_results
        print('Done with Test 1')

    if 2 in run_tests:
        # Apply Test 2
        print('Starting to run Test 2')
        spills_df['Test 2 Status'] = spills_df.apply(lambda row: test2.test_2(row, df, results_ts), axis=1)
        print('Done with Test 2')

    # Classification logic here may need adjustment based on which tests are run
    # This example assumes both tests need to be considered for classification
    def classify_spill(row):
        if 'Test 1 Status' in spills_df.columns and row['Test 1 Status'] == 'Fail':
            return 'Unsatisfactory'
        elif 'Test 2 Status' in spills_df.columns and row['Test 2 Status'] == 'Pass':
            return 'Satisfactory'
        else:
            return 'Substandard'  # Default/fallback classification
    
    spills_df['Classification'] = spills_df.apply(classify_spill, axis=1)
    print('Classification complete')
        
    years = []
    spill_count = [[] for _ in range(3)]

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

    return spills_df, annual_summary



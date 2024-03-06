import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection
import datetime as dt
import numpy as np
import app.gn066_tests.config as config


# Define the period you want to display for the timeline. Math is done for all 10 years
timeline_start = dt.datetime(2020, 1, 1, 0, 0, 0)
timeline_end = dt.datetime(2020, 12, 31, 0, 0, 0)


def timeline_visual(spills_baseline, df, timeline_start, timeline_end):
    """
    Make a pretty time line graph from defined start to finish
    """

    data = df.loc[(df.index >= timeline_start) & (df.index <= timeline_end)]

    # Creating empty lists to store start and end dates for collection of bars
    test_1_bars = []
    test_2_bars = []
    combined_bars = []
    spill_bars = []
    for i in range(1, len(data)):
        # Test 2
        if data.iloc[i]['Spill_allowed?'] == 'YES' and (data.iloc[i-1]['Spill_allowed?'] != 'YES' or i == 1):
            # print (i)
            start_date = data.index[i]
            # print (start_date)
            for j in range(i+1, len(data)):
                if data.iloc[j]['Spill_allowed?'] != 'YES':
                    # print (j)
                    end_date = data.index[j]
                    test_2_bars.append((start_date, end_date, 'Test 2 Pass'))
                    combined_bars.append(
                        (start_date, end_date, 'Satisfactory'))
                    break
                if j == (len(data)-1):
                    end_date = data.index[j]
                    test_2_bars.append((start_date, end_date, 'Test 2 Pass'))
                    combined_bars.append(
                        (start_date, end_date, 'Satisfactory'))
                    break
        elif data.iloc[i]['Spill_allowed?'] != 'YES' and (data.iloc[i-1]['Spill_allowed?'] == 'YES' or i == 1):
            # print (i)
            start_date = data.index[i]
            # print (start_date)
            for j in range(i+1, len(data)):
                if data.iloc[j]['Spill_allowed?'] == 'YES':
                    # print (j)
                    end_date = data.index[j]
                    test_2_bars.append((start_date, end_date, 'Test 2 Fail'))
                    combined_bars.append((start_date, end_date, 'Substandard'))
                    break
                if j == (len(data)-1):
                    end_date = data.index[j]
                    test_2_bars.append((start_date, end_date, 'Test 2 Fail'))
                    combined_bars.append((start_date, end_date, 'Substandard'))
                    break

    for i in range(1, len(data)):
        # Test 1
        if data.iloc[i]['Day Type'] == 'Dry' and (data.iloc[i-1]['Day Type'] != 'Dry' or i == 1):
            start_date = data.index[i]
            for j in range(i+1, len(data)):
                if data.iloc[j]['Day Type'] != 'Dry':
                    end_date = data.index[j]
                    test_1_bars.append((start_date, end_date, 'Test 1 Fail'))
                    combined_bars.append(
                        (start_date, end_date, 'Unsatisfactory'))
                    break
                if j == (len(data)-1):
                    end_date = data.index[j]
                    test_1_bars.append((start_date, end_date, 'Test 1 Fail'))
                    combined_bars.append(
                        (start_date, end_date, 'Unsatisfactory'))
                    break
        if data.iloc[i]['Day Type'] != 'Dry' and (data.iloc[i-1]['Day Type'] == 'Dry' or i == 1):
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

    for i in range(1, len(data)):
        # Spills data
        run_name = spills_baseline[2]
        if data.iloc[i][run_name] == 'YES' and data.iloc[i-1][run_name] != 'YES':
            start_date = data.index[i]
            for j in range(i+1, len(df)):
                if data.iloc[j][run_name] != 'YES':
                    end_date = data.index[j]
                    spill_bars.append((start_date, end_date, run_name))

                    break

    # print (test_1_bars)
    # print (test_2_bars)
    # print (spill_bars)
    bars = test_2_bars + test_1_bars + combined_bars + spill_bars

    # On to graphing
    cycle = ['white', 'forestgreen', 'firebrick', 'darkorange', 'purple', 'navy',
             'blue', 'dodgerblue', 'deepskyblue', 'lightskyblue', ' paleturquoise']
    cats = {"Test 1 Pass": 1, "Test 1 Fail": 1, "Test 2 Pass": 2,
            "Test 2 Fail": 2, "Satisfactory": 3, "Substandard": 3, "Unsatisfactory": 3}
    colormapping = {"Test 1 Pass": cycle[0], "Test 1 Fail": cycle[0], "Test 2 Pass": cycle[0],
                    "Test 2 Fail": cycle[0], "Satisfactory": cycle[1], "Substandard": cycle[3], "Unsatisfactory": cycle[2]}
    y_labels = ["", "", "Classification"]
    cats.update({spills_baseline[2]: 4})
    colormapping.update({spills_baseline[2]: cycle[4]})
    y_labels.append(spills_baseline[2])

    # print (cats)
    # print (colormapping)
    # print (y_labels)

    verts = []
    colors = []
    for bar in bars:
        v = [(mdates.date2num(bar[0]), cats[bar[2]]-.49),
             (mdates.date2num(bar[0]), cats[bar[2]]+.49),
             (mdates.date2num(bar[1]), cats[bar[2]]+.49),
             (mdates.date2num(bar[1]), cats[bar[2]]-.49),
             (mdates.date2num(bar[0]), cats[bar[2]]-.49)]
        verts.append(v)
        colors.append(colormapping[bar[2]])

    library = PolyCollection(verts, facecolors=colors)
    # Create figure
    fig, ax = plt.subplots(figsize=(60, 2))
    ax.add_collection(library)
    ax.autoscale()
    if timeline_end - timeline_start <= dt.timedelta(30, 0):
        loc = mdates.DayLocator(interval=1)
    elif timeline_end - timeline_start <= dt.timedelta(60, 0):
        loc = mdates.DayLocator(bymonthday=[0, 7, 14, 21, 28])
    else:
        loc = mdates.DayLocator(bymonthday=[0, 15, 30])
    days = mdates.DayLocator(interval=1)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_minor_locator(days)
    ax.grid(which='minor', color='#F0F0F0', linewidth=0.5, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(loc))

    ax.set_yticks([i for i in range(1, 5)])
    ax.set_yticklabels(y_labels)
    ax.grid(which='major', axis='x')

    # Add rainfall depth
    ax2 = ax.twinx()
    ax2.plot(data.index, data['Rolling 1hr depth'], 'b-')
    ax2.plot(data.index, np.full(len(data), config.heavy_rain), 'k--')
    ax2.set_ylabel('Rainfall depth over any hour (mm)')
    ax2.set_ylim(0, data['Rolling 1hr depth'].max()*(4)/3)

    plt.show()

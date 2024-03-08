# This file has all been tested in a different branch and functions correctly, however has not yet been implemented
# due to waiting for Sanils merge request so that his code can be tested and implemented first.



# This file contains the test3 function which is used to check compliance with the consented FPF and formula A for a given row of data.

def check_compliance(row, formula_a, consent_fpf):
    peak_pff = row['Peak PFF (l/s)']
    avg_initial_pff = row['Avg Initial PFF (l/s)']

    if consent_fpf is None:  # Automatic pass if no consented FPF is defined
        return 'Satisfactory'
    elif peak_pff < consent_fpf or avg_initial_pff < consent_fpf:
        return 'Unsatisfactory'
    elif peak_pff < formula_a or avg_initial_pff < formula_a:
        return 'Substandard'
    else:
        return 'Satisfactory'

# This code goes in the create_two.html file

# {% endif %} {% if 'test-3' in session.tests %}
#                       <div class="flex-1 space-y-4">
#                         <div>
#                           <label
#                             for="spill-stats"
#                             class="block text-sm font-medium mb-2 dark:text-white"
#                             >Baseline Stats Report</label
#                           >
#                           <input
#                             type="file"
#                             name="Baseline Stats Report"
#                             id="Baseline Stats Report"
#                             required
#                             accept=".xlsx,.csv"
#                             class="block w-auto border border-gray-200 shadow-sm rounded-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600 file:bg-gray-50 file:border-0 file:me-4 file:py-3 file:px-4 dark:file:bg-gray-700 dark:file:text-gray-400"
#                           />
#                         </div>
#                         <div>
#                           <label
#                             for="formula-a"
#                             class="block text-sm font-medium mb-2 dark:text-white"
#                             >Formula A (I/s)</label
#                           >
#                           <input
#                             type="text"
#                             id="formula-a"
#                             name="formula-a"
#                             class="py-3 px-4 block max-w-80 w-5/6 border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200 dark:focus:ring-gray-600"
#                             placeholder="Enter Value"
#                             required
#                           />
#                         </div>
#                         <div>
#                           <label
#                             for="consent-flow"
#                             class="block text-sm font-medium mb-2 dark:text-white"
#                             >Consent Pass Forward Flow (I/s)</label
#                           >
#                           <input
#                             type="text"
#                             id="consent-flow"
#                             name="consent-flow"
#                             class="py-3 px-4 block max-w-80 w-5/6 border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200 dark:focus:ring-gray-600"
#                             placeholder="Enter Value"
#                             required
#                           />
#                         </div>
#                       </div>
#                       {% endif %}
    

# This code goes in the run.py file

    # from app.gn066_tests.tests import test3 

    # form_data = await request.form
    # files = await request.files

    # # Parsing user input for formula A and consent pass forward flow
    # formula_a_value = float(form_data.get('formula-a', 0))
    # consent_flow_value = float(form_data.get('consent-flow', 0))
    
    # baseline_stats_file = files.get('Baseline Stats Report')

    # # Processing the Baseline Stats Report
    # df_pff = pd.read_excel(baseline_stats_file.stream, sheet_name="Summary", header=1)
    
    # df_pff['Compliance Status'] = df_pff.apply(lambda row: test3.check_compliance(row, formula_a_value, consent_flow_value), axis=1)
    
    # print(df_pff[['Year', 'Compliance Status']])

    # html_content = df_pff[['Year', 'Compliance Status']].to_html()
    # return f"hello<br>{html_content}", 200    # return await render_template("runs/create_two.html")

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


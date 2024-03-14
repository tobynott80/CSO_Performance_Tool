# This file contains the test3 function which is used to check compliance with the consented FPF and formula A for a given row of data.

def check_compliance(row, formula_a, consent_fpf):
    peak_pff = row['Peak PFF (l/s)']
    avg_initial_pff = row['Avg Initial PFF (l/s)']

    # Automatic pass if no consented FPF is defined
    if consent_fpf is None:
        return 'Satisfactory'
    # Mark as Unsatisfactory if below Consent FPF
    elif peak_pff < consent_fpf or avg_initial_pff < consent_fpf:
        return 'Unsatisfactory'
    # Check for Substandard: Below Formula A but above Consent FPF (if Consent FPF is lower)
    elif (peak_pff < formula_a or avg_initial_pff < formula_a) and (consent_fpf < formula_a):
        return 'Substandard'
    # Remaining cases are Satisfactory
    else:
        return 'Satisfactory'

    
def check_formula_a(row, formula_a):
    peak_pff = row['Peak PFF (l/s)']
    avg_initial_pff = row['Avg Initial PFF (l/s)']

    if peak_pff < formula_a or avg_initial_pff < formula_a:
        return 'Unsatisfactory'
    else:
        return 'Satisfactory'

def check_consent_fpf(row, consent_fpf):
    peak_pff = row['Peak PFF (l/s)']
    avg_initial_pff = row['Avg Initial PFF (l/s)']

    if consent_fpf is None:  # Automatic pass if no consented FPF is defined
        return 'Satisfactory'
    elif peak_pff < consent_fpf or avg_initial_pff < consent_fpf:
        return 'Unsatisfactory'
    else:
        return 'Satisfactory'


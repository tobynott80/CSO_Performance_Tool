# This file contains the test3 function which is used to check compliance with the consented FPF and formula A for a given row of data.

def check_compliance(row, formula_a, consent_fpf):
    peak_pff = row['Peak PFF (l/s)']
    avg_initial_pff = row['Avg Initial PFF (l/s)']

    # Evaluate against formula_a if consent_fpf is None
    if consent_fpf is None:
        if formula_a is not None:  # Ensure formula_a is checked when consent_fpf is None
            if peak_pff < formula_a or avg_initial_pff < formula_a:
                return 'Unsatisfactory'
            else:
                return 'Satisfactory'
        else:
            return 'Satisfactory'  # Automatic pass if consent_fpf is None and formula_a is not applicable

    # If consent_fpf is provided, check compliance based on the provided logic
    if peak_pff < consent_fpf or avg_initial_pff < consent_fpf:
        return 'Unsatisfactory'
    elif formula_a is not None and (peak_pff < formula_a or avg_initial_pff < formula_a):
        # Substandard check requires knowing if formula_a is provided and is less than peak or avg initial pff
        return 'Substandard'
    else:
        return 'Satisfactory'
    
def check_formula_a(row, formula_a):
    if formula_a is None:
        return 'None'  # Return 'None' if no formula_a value is provided

    peak_pff = row['Peak PFF (l/s)']
    avg_initial_pff = row['Avg Initial PFF (l/s)']

    if peak_pff < formula_a or avg_initial_pff < formula_a:
        return 'Unsatisfactory'
    else:
        return 'Satisfactory'

def check_consent_fpf(row, consent_fpf):
    if consent_fpf is None:
        return 'None'  # Return 'None' if no consent_fpf value is provided

    peak_pff = row['Peak PFF (l/s)']
    avg_initial_pff = row['Avg Initial PFF (l/s)']

    if peak_pff < consent_fpf or avg_initial_pff < consent_fpf:
        return 'Unsatisfactory'
    else:
        return 'Satisfactory'


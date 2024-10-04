import pandas as pd

# Assuming dataframes is your list of DataFrames and 'Mass' is the column name for the m/z values
def trim_spectra(dataframes, mz_range):
    trimmed_dataframes = []
    lower_bound, upper_bound = mz_range
    
    for df in dataframes:
        trimmed_df = df[(df['Mass'] >= lower_bound) & (df['Mass'] <= upper_bound)]        
        trimmed_dataframes.append(pd.DataFrame(trimmed_df))
    
    return trimmed_dataframes
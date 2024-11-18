import numpy as np
import pandas as pd
# import pybaselines
from pybaselines import Baseline

def snip_baseline_correction(dataframes, iterations=30):
    snipped_dataframes = []

    for df in dataframes:
        n = len(df)
        baseline = np.copy(df['Intensity'].values)  # Assuming you want to correct 'Intensity'
    
        for i in range(iterations):
            for j in range(1, n - 1):
                # Use np.minimum to get the element-wise minimum
                baseline[j] = np.minimum(baseline[j], (baseline[j - 1] + baseline[j + 1]) / 2)

        # Create a new DataFrame with 'mass' and corrected 'Intensity'
        corrected_df = df.copy()
        corrected_df['Baseline'] = baseline
        
        snipped_dataframes.append(corrected_df)

    return snipped_dataframes


def apply_snip_baseline_correction(spectra_list, window_size=10):
    """
    Applies SNIP baseline correction to a list of mass spec data DataFrames.

    Parameters:
    spectra_list (list of pd.DataFrame): A list of dataframes containing mass spec data.
    Each dataframe should have two columns: m/z and intensity.
    window_size (int): The size of the moving average window for smoothing the baseline.

    Returns:
    list of pd.DataFrame: A list of baseline-corrected spectra as dataframes.
    """
    corrected_spectra_list = []

    # Iterate over each spectrum in the list
    for index, spectrum_df in enumerate(spectra_list):
        # Ensure that the DataFrame has at least two columns
        if spectrum_df.shape[1] < 2:
            raise ValueError(f"DataFrame at index {index} must contain at least two columns: m/z and intensity.")
        
        # Extract x and y values (m/z and intensity)
        x = spectrum_df.iloc[:, 0].values
        y = spectrum_df.iloc[:, 1].values

        # Check if x and y are valid
        if x.ndim != 1 or y.ndim != 1:
            raise ValueError(f"m/z and intensity values in DataFrame {index} must be one-dimensional arrays.")
        
        # Apply SNIP algorithm to get the baseline
        try:
            baseline_fitter = Baseline(x_data=x)
            baseline, params = baseline_fitter.snip(y, max_half_window=20)
        except Exception as e:
            raise RuntimeError(f"An error occurred while applying SNIP to DataFrame {index}: {e}")
        
        # Smooth the baseline using a moving average
        smoothed_baseline = np.convolve(baseline, np.ones(window_size) / window_size, mode='same')

        # Ensure smoothed_baseline has the same length as y
        if smoothed_baseline.shape != y.shape:
            raise ValueError(f"The smoothed baseline and intensity in DataFrame {index} must have the same length.")
        
        # Subtract the smoothed baseline from the original intensity
        corrected_spectrum = y - smoothed_baseline
        
        # Store the corrected spectrum in a new DataFrame
        corrected_spectrum_df = pd.DataFrame({'Mass': x, 'Intensity': y, 'Baseline': y - corrected_spectrum})
        
        # Add the corrected DataFrame to the list
        corrected_spectra_list.append(corrected_spectrum_df)
    
    return corrected_spectra_list
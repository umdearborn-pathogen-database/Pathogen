import numpy as np
import pandas as pd
import pybaselines
from pybaselines import Baseline

# this only takes in a single dataframe. We need to do this over all of the dataframes. Look at the method below.
# def snip_baseline_correction(signal, iterations=150):
#     n = len(signal)
#     baseline = np.copy(signal)
    
#     for i in range(iterations):
#         for j in range(1, n - 1):
#             baseline[j] = min(baseline[j], (baseline[j - 1] + baseline[j + 1]) / 2)
    
#     return baseline

# this is too much processing, replacing this with below for now
# def snip_baseline_correction(dataframes, iterations=150):
#     snipped_dataframes = []

#     for df in dataframes:
#         n = len(df)
#         baseline = np.copy(df)
    
#         for i in range(iterations):
#             for j in range(1, n - 1):
#                 baseline[j] = min(baseline[j], (baseline[j - 1] + baseline[j + 1]) / 2)

#         snipped_dataframes.append(baseline)

#     return trimmed_dataframes

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
        # x = spectrum_df["Mass"].values
        # y = spectrum_df["Intensity"].values

        # Print shapes for debugging
        print(f"Processing DataFrame {index}:")
        print(f"x shape: {x.shape}, y shape: {y.shape}")
        print(f"x type: {type(x)}, y type:  {type(y)}")
        
        # Check if x and y are valid
        if x.ndim != 1 or y.ndim != 1:
            raise ValueError(f"m/z and intensity values in DataFrame {index} must be one-dimensional arrays.")
        
        # Apply SNIP algorithm to get the baseline
        try:
            baseline_fitter = Baseline(x_data=x)
            baseline, params = baseline_fitter.snip(y, max_half_window=20)
            # snip_baseline = baseline.snip(decreasing=True)
            print(f"SNIP baseline shape for DataFrame {index}: {baseline.shape}")
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

# def snip_baseline_correction(dataframes, iterations=150, threshold=1e-6):
#     snipped_dataframes = []

#     for df in dataframes:
#         baseline = np.copy(df)

#         for _ in range(iterations):
#             # Compute the baseline for the interior points
#             new_baseline = np.minimum(baseline[1:-1], (baseline[:-2] + baseline[2:]) / 2)
#             new_baseline = np.concatenate(([baseline[0]], new_baseline, [baseline[-1]]))  # Maintain the original shape
            
#             # Check for convergence (stop if the change is small)
#             if np.max(np.abs(new_baseline - baseline)) < threshold:
#                 break

#             baseline = new_baseline

#         snipped_dataframes.append(baseline)

#     return snipped_dataframes

# def snip_baseline_correction(ms_data_list, iterations=100):
#     """
#     Perform SNIP (Statistics-sensitive Non-linear Iterative Peak-clipping) baseline correction
#     on a list of mass spectrometry data (mass and intensity pairs).

#     Parameters:
#     ms_data_list (list of dicts): A list of mass spec data, where each entry is a dictionary 
#                                   containing 'mass' and 'intensity' arrays.
#     iterations (int): The number of iterations to perform (default: 100).

#     Returns:
#     list of dicts: A list of corrected mass spec data, where 'mass' is preserved and 
#                    'intensity' is baseline-corrected.
#     """
#     corrected_data_list = []

#     for data in ms_data_list:
#         mass = data['Mass']
#         intensity = data['Intensity']
        
#         # Ensure intensity is a NumPy array
#         intensity = np.array(intensity)
        
#         # Initialize baseline with the intensity values
#         baseline = intensity.copy()
        
#         # Length of the intensity data
#         n = len(intensity)
        
#         # Perform iterative peak clipping
#         for k in range(1, iterations + 1):
#             half_window = int(k / 2)
#             for i in range(half_window, n - half_window):
#                 # Compare current baseline value with the average of surrounding values
#                 baseline[i] = min(baseline[i], 
#                                   0.5 * (baseline[i - half_window] + baseline[i + half_window]))
        
#         # Subtract the estimated baseline from the original intensity
#         corrected_intensity = intensity - baseline
        
#         # Ensure no negative values in the corrected spectrum
#         corrected_intensity[corrected_intensity < 0] = 0
        
#         # Append the corrected mass and intensity to the result list
#         corrected_data_list.append({
#             'Mass': mass,
#             'Intensity': corrected_intensity
#         })
    
#     return corrected_data_list

# def snip_baseline_correction(y, iterations=150, decreasing=False):
#     """
#     SNIP baseline correction translated from C to Python.
    
#     Args:
#     y: np.array of spectra intensity values (double values).
#     iterations: maximum number of iteration steps (default: 150).
#     decreasing: whether to use a decreasing clipping window (default: False).
    
#     Returns:
#     np.array with baseline corrected values.
#     """
#     # Ensure y is a numpy array and make a copy for output
#     y = np.asarray(y, dtype=np.float64)
#     n = len(y)
#     output = np.copy(y)
    
#     # Perform SNIP baseline correction
#     for i in range(iterations if decreasing else 1, 0 if decreasing else iterations + 1):
#         for j in range(i, n - i):
#             # Compute the average of the surrounding values
#             a = y[j]
#             b = (y[j - i] + y[j + i]) / 2
#             # Set the new baseline point if the average is lower
#             output[j] = min(a, b)

#         # Update y for the next iteration
#         y[i:n-i] = output[i:n-i]

#     return output


# going back to top algo
# def snip_baseline_correction(dataframes, column_name="Intensity", iterations=150, decreasing=False):
#     """
#     SNIP baseline correction for a list of DataFrames.

#     Args:
#     dataframes: List of DataFrames, each containing spectra data.
#     column_name: The name of the column with intensity values (default: "intensity").
#     iterations: Maximum number of iteration steps (default: 150).
#     decreasing: Whether to use a decreasing clipping window (default: False).

#     Returns:
#     List of DataFrames with baseline corrected intensity values.
#     """
#     corrected_dataframes = []

#     for df in dataframes:
#         # Make sure the column exists in the DataFrame
#         if column_name not in df.columns:
#             raise ValueError(f"Column '{column_name}' not found in DataFrame")

#         # Extract the intensity data as a NumPy array
#         y = df[column_name].to_numpy(dtype=np.float64)
#         n = len(y)
#         output = np.copy(y)
        
#         # Perform SNIP baseline correction
#         for i in range(iterations if decreasing else 1, 0 if decreasing else iterations + 1):
#             for j in range(i, n - i):
#                 # Compute the average of the surrounding values
#                 a = y[j]
#                 b = (y[j - i] + y[j + i]) / 2
#                 # Set the new baseline point if the average is lower
#                 output[j] = min(a, b)

#             # Update y for the next iteration
#             y[i:n-i] = output[i:n-i]

#         # Create a new DataFrame with the corrected values
#         corrected_df = df.copy()
#         corrected_df[column_name] = output

#         # Append the corrected DataFrame to the list
#         corrected_dataframes.append(corrected_df)

#     return corrected_dataframes
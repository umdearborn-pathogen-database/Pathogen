import numpy as np
from scipy.signal import find_peaks
import statsmodels.api as sm
import pandas as pd

from Helper.Helper import print_dataframe_summary
from Dependencies.Global import printMessage

# def alignSpectra(spectra_list, halfWindowSize=20, noiseMethod="MAD", SNR=2, reference=None, tolerance=0.002, warpingMethod="lowess", allowNoMatches=False, emptyNoMatches=False, **kwargs):
#     alignedSpectra = []  # To hold the aligned spectra from each DataFrame

#     for spectra in spectra_list:
#         # Detect peaks for the current DataFrame
#         peaks = detectPeaks(spectra, halfWindowSize=halfWindowSize, noiseMethod=noiseMethod, SNR=SNR)
#         warpingFunctions = []
#         x = peaks['Mass']
#         d = np.zeros_like(x)

#         # Determine the warping function based on the specified method
#         if warpingMethod == "lowess":
#             wf = warpingFunctionLowess(x, d, **kwargs)
#         elif warpingMethod == "linear":
#             wf = warpingFunctionLinear(x, d, **kwargs)
#         elif warpingMethod == "quadratic":
#             wf = warpingFunctionQuadratic(x, d, **kwargs)
#         elif warpingMethod == "cubic":
#             wf = warpingFunctionCubic(x, d, **kwargs)
#         else:
#             printMessage("err", f"Unknown warping method: {warpingMethod}")
#             wf = None

#         warpingFunctions.append(wf)

#         # Warp the mass spectra for the current DataFrame
#         alignedSpectra.append(warpMassSpectra([spectra], warpingFunctions, emptyNoMatches=emptyNoMatches))

#     return alignedSpectra



# def detectPeaks(spectra, halfWindowSize=20, noiseMethod="MAD", SNR=2):
#     # mass = spectrum_df['mass'].values
#     # intensity = spectrum_df['intensity'].values

#     intensity = spectra['Intensity'].values
#     mass = spectra['Mass'].values
#     peakIndices, _ = find_peaks(intensity, distance=halfWindowSize)
#     return {'Mass': mass[peakIndices], 'Intensity': intensity[peakIndices]}

# def warpingFunctionLowess(x, d, **kwargs):
#     lowess = sm.nonparametric.lowess(d, x, **kwargs)
#     if lowess.ndim != 2 or lowess.shape[1] != 2:
#         printMessage("err", ValueError("Lowess result is not a 2D array with two columns."))
#     return lowess

# def warpingFunctionLinear(x, d, **kwargs):
#     coeffs = np.polyfit(x, d, 1)
#     return np.poly1d(coeffs)

# def warpingFunctionQuadratic(x, d, **kwargs):
#     coeffs = np.polyfit(x, d, 2)
#     return np.poly1d(coeffs)

# def warpingFunctionCubic(x, d, **kwargs):
#     coeffs = np.polyfit(x, d, 3)
#     return np.poly1d(coeffs)

# def warpMassSpectra(spectra, warpingFunctions, emptyNoMatches=False):
#     warpedSpectra = []
#     for spectrum, wf in zip(spectra, warpingFunctions):
#         if wf is None:
#             if emptyNoMatches:
#                 warpedSpectra.append({'Mass': spectrum['Mass'], 'Intensity': np.zeros_like(spectrum['Mass'])})
#             continue
#         mass = spectrum["Mass"].values
#         intensity = spectrum["Intensity"].values
#         print("warpingfunctions", warpingFunctions)
#         print(f"type of mass:{type(mass)} type of wf{type(wf)}")
#         warpedMass = mass + wf(mass)
#         warpedSpectra.append({'Mass': warpedMass, 'Intensity': intensity})
#     return warpedSpectra
	

# def detect_peaks(spectrum_df, half_window_size=20, noise_method="MAD", SNR=2):
#     # Placeholder for a peak detection implementation
#     # This should return a DataFrame containing detected peaks and their masses
#     # Here we will just simulate peak detection for demonstration
#     # Replace this with your actual peak detection logic
#     mass = spectrum_df['Mass'].values
#     intensity = spectrum_df['Intensity'].values
#     peaks = (intensity > np.median(intensity) + SNR * np.std(intensity)).astype(int)
#     peak_positions = mass[peaks.astype(bool)]
#     return pd.DataFrame({'Mass': peak_positions})

# def determine_warping_functions(peaks, reference=None, tolerance=0.002, method="lowess"):
#     # Placeholder for a warping function determination logic
#     # This should return a list of warping functions based on the detected peaks
#     # For simplicity, we will return a dummy function that does nothing
#     def dummy_warp(mass):
#         return np.zeros_like(mass)  # No warping applied
#     return [dummy_warp] * len(peaks)  # Dummy warping functions for each spectrum

# def warp_mass_spectra(spectra, warping_functions):
#     warped_spectra = []
#     for spectrum, wf in zip(spectra, warping_functions):
#         mass = spectrum['Mass'].values
#         intensity = spectrum['Intensity'].values
#         warped_mass = mass + wf(mass)  # Apply the warping function
#         warped_spectra.append({'Mass': warped_mass, 'Intensity': intensity})
#     return warped_spectra

# def align_peaks(spectra_list, half_window_size=20, noise_method="MAD", SNR=2, 
#                 reference=None, tolerance=0.002, warping_method="lowess"):
#     """
#     Aligns peaks in a list of mass spectra DataFrames.

#     Parameters:
#     - spectra_list (List[pd.DataFrame]): A list of DataFrames containing mass and intensity data.
#     - half_window_size (int): Half the size of the window for peak detection.
#     - noise_method (str): The method used for noise estimation.
#     - SNR (float): Signal-to-noise ratio for peak detection.
#     - reference (pd.DataFrame): A reference DataFrame for alignment.
#     - tolerance (float): Tolerance for matching peaks.
#     - warping_method (str): The method used for warping.

#     Returns:
#     List[dict]: A list of aligned mass spectra with 'Mass' and 'Intensity'.
#     """
    
#     # Check if input is a list of DataFrames
#     # if not isinstance(spectra_list, list) or not all(isinstance(spectrum, pd.DataFrame) for spectrum in spectra_list):
#     #     raise ValueError("Input must be a list of mass spectra DataFrames.")

#     # Detect peaks in each spectrum
#     peaks = [detect_peaks(spectrum, half_window_size, noise_method, SNR) for spectrum in spectra_list]

#     # Determine warping functions based on detected peaks
#     warping_functions = determine_warping_functions(peaks, reference=reference, tolerance=tolerance, method=warping_method)

#     # Warp the mass spectra using the determined warping functions
#     aligned_spectra = warp_mass_spectra(spectra_list, warping_functions)

#     return aligned_spectra



# NEWEST COMMENT OUT

def align_peaks(spectra_list, half_window_size=20, noise_method="MAD", SNR=2, 
                reference=None, tolerance=0.002, warping_method="lowess"):
    """
    Aligns peaks in a list of mass spectra DataFrames.

    Parameters:
    - spectra_list (List[pd.DataFrame]): A list of DataFrames containing mass and intensity data.
    - half_window_size (int): Half the size of the window for peak detection.
    - noise_method (str): The method used for noise estimation.
    - SNR (float): Signal-to-noise ratio for peak detection.
    - reference (pd.DataFrame): A reference DataFrame for alignment.
    - tolerance (float): Tolerance for matching peaks.
    - warping_method (str): The method used for warping.

    Returns:
    List[pd.DataFrame]: A list of aligned mass spectra DataFrames with 'Mass' and 'Intensity'.
    """
    # Check if input is a list of DataFrames
    if not isinstance(spectra_list, list) or not all(isinstance(spectrum, pd.DataFrame) for spectrum in spectra_list):
        raise ValueError("Input must be a list of mass spectra DataFrames.")

    # Detect peaks in each spectrum
    peaks = [detect_peaks(spectrum, half_window_size, noise_method, SNR) for spectrum in spectra_list]

    # Determine warping functions based on detected peaks
    warping_functions = determine_warping_functions(peaks, reference=reference, tolerance=tolerance, method=warping_method)

    # Warp the mass spectra using the determined warping functions
    aligned_spectra = warp_mass_spectra(spectra_list, warping_functions)

    return aligned_spectra

def detect_peaks(spectrum_df, half_window_size=20, noise_method="MAD", SNR=2):
    # Placeholder for peak detection implementation
    mass = spectrum_df['Mass'].values
    intensity = spectrum_df['Intensity'].values
    
    # Simple peak detection based on SNR
    threshold = np.median(intensity) + SNR * np.std(intensity)
    peaks = intensity > threshold
    
    # Extract peak positions
    peak_positions = mass[peaks]
    return pd.DataFrame({'Mass': peak_positions})

def determine_warping_functions(peaks, reference=None, tolerance=0.002, method="lowess"):
    # Placeholder for determining warping functions
    # In practice, implement the logic to calculate warping functions based on peaks
    return [None] * len(peaks)  # Replace with actual warping functions

def warp_mass_spectra(spectra, warping_functions):
    warped_spectra = []
    for spectrum, wf in zip(spectra, warping_functions):
        if wf is None:  # If no warping function, append original spectrum
            warped_spectra.append(spectrum)
            continue

        mass = spectrum['Mass'].values
        intensity = spectrum['Intensity'].values
        
        # Placeholder for applying the warping function
        # Assuming wf is a function that takes mass and returns warped mass
        warped_mass = mass + wf(mass)  # Adjust this based on how you define wf
        
        # Create a new DataFrame for the warped spectrum
        warped_spectrum = pd.DataFrame({'Mass': warped_mass, 'Intensity': intensity})
        warped_spectra.append(warped_spectrum)
    
    return warped_spectra


# def detectPeaksInDataframe(df, half_window_size=20, method="MAD", SNR=2):
#     """
#     Detect peaks in a single DataFrame based on SNR and local maxima.
    
#     Parameters:
#         df (pd.DataFrame): DataFrame containing 'Mass', 'Intensity', and 'patientID' columns.
#         half_window_size (int): Window size for detecting local maxima.
#         method (str): Method for noise estimation, e.g., "MAD".
#         SNR (float): Signal-to-noise ratio threshold for peak detection.
    
#     Returns:
#         pd.DataFrame: A DataFrame containing detected peaks with 'Mass', 'Intensity', and SNR.
#     """
#     # Check for an empty spectrum
#     if df.empty or df['Intensity'].isnull().all():
#         return df[['Mass', 'Intensity']].copy()  # Empty or non-signal DataFrame
    
#     # Estimate noise based on the selected method
#     noise = estimateNoise(df['Intensity'], method=method)
    
#     # Find local maxima within the specified window
#     is_local_maxima = findLocalMaxima(df['Intensity'], half_window_size=half_window_size)
    
#     # Only keep points where intensity is above noise level and is a local maxima
#     is_above_noise = df['Intensity'] > (SNR * noise)
#     peak_indices = df.index[is_local_maxima & is_above_noise]
    
#     # Return DataFrame of detected peaks
#     peak_df = df.loc[peak_indices, ['Mass', 'Intensity']].copy()
#     peak_df['SNR'] = df.loc[peak_indices, 'Intensity'] / noise[peak_indices]
    
#     return peak_df

def detectPeaksInDataframe(df, half_window_size=20, method="MAD", SNR=2):
    """
    Detect peaks in a single DataFrame based on SNR and local maxima.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing 'Mass', 'Intensity', and 'patientID' columns.
        half_window_size (int): Window size for detecting local maxima.
        method (str): Method for noise estimation, e.g., "MAD".
        SNR (float): Signal-to-noise ratio threshold for peak detection.
    
    Returns:
        pd.DataFrame: A DataFrame containing detected peaks with 'Mass', 'Intensity', and SNR.
    """
    # Check for an empty spectrum
    if df.empty or df['Intensity'].isnull().all():
        return df[['Mass', 'Intensity']].copy()  # Empty or non-signal DataFrame
    
    # Estimate noise based on the selected method
    noise = estimateNoise(df['Intensity'], method=method)
    if not isinstance(noise, pd.Series):
        # If noise is a scalar, repeat it for the length of df to make element-wise operations possible
        noise = pd.Series([noise] * len(df), index=df.index)
    
    # Find local maxima within the specified window
    is_local_maxima = findLocalMaxima(df['Intensity'], half_window_size=half_window_size)
    
    # Only keep points where intensity is above noise level and is a local maxima
    is_above_noise = df['Intensity'] > (SNR * noise)
    peak_indices = df.index[is_local_maxima & is_above_noise]
    
    # Return DataFrame of detected peaks
    peak_df = df.loc[peak_indices, ['Mass', 'Intensity','patientID','Bacteria']].copy()
    peak_df['SNR'] = df.loc[peak_indices, 'Intensity'] / noise.loc[peak_indices]
    
    return peak_df

def detectPeaksInList(dataframes, half_window_size=20, method="MAD", SNR=2):
    """
    Applies detect_peaks_in_dataframe to each DataFrame in a list.
    
    Parameters:
        dataframes (list of pd.DataFrame): List of DataFrames containing 'Mass', 'Intensity', and 'patientID'.
    
    Returns:
        list of pd.DataFrame: List of DataFrames with detected peaks for each original DataFrame.
    """
    return [detectPeaksInDataframe(df, half_window_size=half_window_size, method=method, SNR=SNR) for df in dataframes]

# Placeholder for noise estimation based on method
def estimateNoise(intensity, method="MAD"):
    if method == "MAD":
        # Calculate MAD (Mean Absolute Deviation) for Series
        return abs(intensity - intensity.median()).mean()
    elif method == "SuperSmoother":
        # Placeholder for an actual SuperSmoother calculation
        return intensity.mean()
    else:
        raise ValueError("Unknown noise estimation method.")

# Placeholder for local maxima detection
def findLocalMaxima(intensity, half_window_size=20):
    # Simple local maxima placeholder
    return (intensity > intensity.shift(1)) & (intensity > intensity.shift(-1))
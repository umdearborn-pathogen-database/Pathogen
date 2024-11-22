import numpy as np
import pandas as pd

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
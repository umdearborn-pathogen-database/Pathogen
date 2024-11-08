import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from typing import List

# def is_mass_peaks_list(peaks):
#     """
#     Check if the input is a valid list of MassPeaks objects.
#     This is a placeholder implementation - modify based on your actual MassPeaks class.
    
#     Args:
#         peaks: List of objects to check
        
#     Returns:
#         bool: True if valid, raises exception if invalid
#     """
#     # Implement your validation logic here
#     if not isinstance(peaks, list):
#         raise TypeError("Input must be a list of MassPeaks objects")
#     # Add additional validation as needed
#     return True

# def is_mass_spectrum_list(spectra):
#     """
#     Check if the input is a valid list of MassSpectrum objects.
#     This is a placeholder implementation - modify based on your actual MassSpectrum class.
    
#     Args:
#         spectra: List of objects to check
        
#     Returns:
#         bool: True if valid, raises exception if invalid
#     """
#     # Implement your validation logic here
#     if not isinstance(spectra, list):
#         raise TypeError("Input must be a list of MassSpectrum objects")
#     # Add additional validation as needed
#     return True

# def as_matrix_mass_object_list(peaks):
#     """
#     Convert a list of MassPeaks objects into a matrix.
#     This is a placeholder implementation - modify based on your actual MassPeaks class.
    
#     Args:
#         peaks: List of MassPeaks objects
        
#     Returns:
#         np.ndarray: Matrix representation of the peaks
#     """
#     # Implement your conversion logic here
#     # This should return a numpy array representing the matrix
#     pass

# def intensity_matrix(peaks, spectra):
#     """
#     Convert a list of MassPeaks into an expression matrix.
    
#     Args:
#         peaks: List of MassPeaks objects
#         spectra: Optional list of MassSpectrum objects
        
#     Returns:
#         np.ndarray: Matrix containing intensity values
        
#     Raises:
#         TypeError: If inputs are not of correct type
#         ValueError: If number of peaks and spectra don't match
#     """
#     # Validate peaks argument
#     is_mass_peaks_list(peaks)
    
#     # Convert peaks to matrix
#     m = as_matrix_mass_object_list(peaks)
    
#     print(type(m))  # Check the type
#     print(m.shape)  # Check the shape of the array
#     print(m)         # Check the content of m

#     # Process spectra if provided
#     if spectra is not None:
#         # Validate spectra argument
#         is_mass_spectrum_list(spectra)
        
#         if len(peaks) != len(spectra):
#             raise ValueError("Incompatible number of spectra!")
        
#         # Find NA values in matrix
#         is_na = np.isnan(m)
#         unique_mass = np.array(m.dtype.names, dtype=float)
        
#         # Create interpolation functions for each spectrum
#         approx_spectra = [
#             interp1d(spectrum.x, spectrum.y, 
#                     bounds_error=False, 
#                     fill_value=0.0) 
#             for spectrum in spectra
#         ]
        
#         # Fill in missing values using interpolation
#         for i, approx in enumerate(approx_spectra):
#             na_indices = is_na[i, :]
#             if np.any(na_indices):
#                 m[i, na_indices] = approx(unique_mass[na_indices])
    
#     return m


def validate_peak_dataframes(peaks: List[pd.DataFrame]) -> bool:
    """
    Validate that each DataFrame in the peaks list has the required columns.
    
    Args:
        peaks: List of DataFrames to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If DataFrames don't have required columns
    """
    required_columns = {'Mass', 'Intensity', 'patientID', 'Bacteria', 'SNR'}
    
    if not isinstance(peaks, list) or not all(isinstance(df, pd.DataFrame) for df in peaks):
        raise ValueError("Input must be a list of pandas DataFrames")
        
    for i, df in enumerate(peaks):
        missing_cols = required_columns - set(df.columns)
        if missing_cols:
            raise ValueError(f"DataFrame at index {i} is missing columns: {missing_cols}")
    
    return True

def validate_spectra_dataframes(spectra: List[pd.DataFrame]) -> bool:
    """
    Validate that each DataFrame in the spectra list has the required columns.
    
    Args:
        spectra: List of DataFrames to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If DataFrames don't have required columns
    """
    required_columns = {'Mass', 'Intensity', 'patientID', 'Bacteria'}
    
    if not isinstance(spectra, list) or not all(isinstance(df, pd.DataFrame) for df in spectra):
        raise ValueError("Input must be a list of pandas DataFrames")
        
    for i, df in enumerate(spectra):
        missing_cols = required_columns - set(df.columns)
        if missing_cols:
            raise ValueError(f"DataFrame at index {i} is missing columns: {missing_cols}")
    
    return True

def create_intensity_matrix(peaks: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Convert list of peak DataFrames into a matrix where rows are samples and columns are mass values.
    
    Args:
        peaks: List of DataFrames containing peak data
        
    Returns:
        pd.DataFrame: Matrix of intensity values
    """
    # Get unique mass values across all peaks
    all_masses = pd.concat([df['Mass'] for df in peaks]).unique()
    all_masses.sort()
    
    # Create empty matrix with samples as rows and mass values as columns
    matrix_data = []
    
    for df in peaks:
        row = pd.Series(index=all_masses, dtype=float)
        row[df['Mass']] = df['Intensity']
        matrix_data.append(row)
    
    return pd.DataFrame(matrix_data, columns=all_masses)

def intensity_matrix(peaks: List[pd.DataFrame], spectra: List[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Convert a list of peak DataFrames into an expression matrix, with optional interpolation
    from spectra DataFrames for missing values.
    
    Args:
        peaks: List of DataFrames containing peak data
        spectra: Optional list of DataFrames containing spectrum data
        
    Returns:
        pd.DataFrame: Matrix of intensity values
        
    Raises:
        ValueError: If inputs are invalid or incompatible
    """
    # Validate inputs
    validate_peak_dataframes(peaks)
    
    # Create initial matrix from peaks
    m = create_intensity_matrix(peaks)
    
    # Process spectra if provided
    if spectra is not None:
        validate_spectra_dataframes(spectra)
        
        if len(peaks) != len(spectra):
            raise ValueError("Incompatible number of spectra!")
        
        # Find NA values in matrix
        is_na = m.isna()
        mass_values = m.columns.astype(float)
        
        # Create interpolation functions for each spectrum
        approx_spectra = []
        for spectrum_df in spectra:
            # Sort by Mass to ensure proper interpolation
            spectrum_df = spectrum_df.sort_values('Mass')
            approx = interp1d(spectrum_df['Mass'], 
                            spectrum_df['Intensity'],
                            bounds_error=False,
                            fill_value=0.0)
            approx_spectra.append(approx)
        
        # Fill in missing values using interpolation
        for i, approx in enumerate(approx_spectra):
            na_indices = is_na.iloc[i]
            if na_indices.any():
                missing_masses = mass_values[na_indices]
                m.iloc[i, na_indices] = approx(missing_masses)
    
    return m
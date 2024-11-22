import pandas as pd
from scipy.interpolate import interp1d
from typing import List

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
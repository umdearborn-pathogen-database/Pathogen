import pandas as pd
import numpy as np
from scipy.interpolate import interp1d


def averageMassSpectra(list_dataframes, labels, method="mean"):
    """
    Averages or sums mass spectra data by given labels.
    
    Parameters:
    l (list): List of pandas DataFrames containing mass spectra data.
    labels (list): List of labels for grouping the DataFrames.
    method (str): Aggregation method to use, either 'mean', 'median', or 'sum'.
    
    Returns:
    list: List of pandas DataFrames, each representing aggregated values for a label.
    """
    # Check if method is valid
    if method not in ["mean", "median", "sum"]:
        raise ValueError("Method must be one of 'mean', 'median', or 'sum'.")
    
    # Ensure all elements in the list are DataFrames
    if not all(isinstance(df, pd.DataFrame) for df in list_dataframes):
        raise ValueError("All items in the list must be pandas DataFrames.")

    labels_list = labels.tolist()  # or labels.values
    
    # Concatenate the list of DataFrames into one
    df_combined = pd.concat(list_dataframes, keys=labels_list, names=['Mass', 'Intensity'])
    
    # Group by 'Label' and aggregate accordingly
    grouped = df_combined.groupby('Label')
    
    # Create a list to store the results
    results = []
    
    # Iterate through each group and apply the aggregation method
    for label, group in grouped:
        if method == "mean":
            aggregated = group.mean().reset_index()  # Compute mean and reset index
        elif method == "median":
            aggregated = group.median().reset_index()  # Compute median and reset index
        elif method == "sum":
            aggregated = group.sum().reset_index()  # Compute sum and reset index
        
        # Add the label as a new column
        aggregated['Label'] = label
        
        # Append the resulting DataFrame to the list
        results.append(aggregated)
    
    return results


def estimateNoise(df):
    """
    Estimates noise in the data by calculating the Median Absolute Deviation (MAD) for each column.
    
    Parameters:
    df (pd.DataFrame): Input DataFrame containing numeric data.
    
    Returns:
    pd.Series: A Series containing the MAD for each column in the DataFrame.
    """
    # Calculate the median of each column
    # median = df.median()
    # medians = [df[['Mass', 'Intensity']].median() for df in dataframes]
    df_for_median = df[['Mass', 'Intensity']]

    median = df_for_median.median()
    
    # Calculate the absolute deviation from the median
    deviation = (df - median).abs()
    
    # Calculate the median of the absolute deviations (MAD)
    mad = deviation.median()
    
    return mad


def binPeaks(peak_list, method="strict", tolerance=0.002):
    """
    Binning peaks by splitting at the largest gap. This is a wrapper around the 
    .binPeaks function which prepares the peak list before and recreates a 
    correct peak list after binning.
    
    Parameters:
    peak_list (list): List of MassPeaks objects (each as a dictionary with 'mass', 'intensity', 'snr').
    method (str): Method for grouping ('strict', 'relaxed', 'reference').
    tolerance (float): Maximum deviation of a peak position to be considered as the same peak.
    
    Returns:
    list: A list of adjusted MassPeaks objects.
    """
    if method not in ["strict", "relaxed", "reference"]:
        raise ValueError("Method must be one of 'strict', 'relaxed', or 'reference'.")

    non_empty = [len(peaks['Mass']) != 0 for peaks in peak_list]
    samples = [i for i, peaks in enumerate(peak_list) for _ in range(len(peaks['Mass']))]

    # Fetch all mass, intensities, and snr
    mass = np.concatenate([peaks['Mass'] for i, peaks in enumerate(peak_list) if non_empty[i]])
    intensities = np.concatenate([peaks['Intensity'] for i, peaks in enumerate(peak_list) if non_empty[i]])
    snr = np.concatenate([peaks['SNR'] for i, peaks in enumerate(peak_list) if non_empty[i]])
    bacteria = np.concatenate([peaks['Bacteria'] for i, peaks in enumerate(peak_list) if non_empty[i]])

    # Sort values by mass
    sorted_idx = np.argsort(mass)
    mass = mass[sorted_idx]
    intensities = intensities[sorted_idx]
    snr = snr[sorted_idx]
    bacteria = bacteria[sorted_idx]
    samples = np.array(samples)[sorted_idx]

    # Select the appropriate grouper function
    if method == "strict":
        grouper = grouperStrict
    elif method == "relaxed":
        grouper = grouperRelaxed
    elif method == "reference":
        grouper = grouperRelaxedHighestAtReference

    # Binning peaks
    mass = _binPeaks(mass=mass, intensities=intensities, samples=samples,
                     tolerance=tolerance, grouper=grouper)

    # Resort mass if method is not strict
    if method != "strict":
        sorted_idx = np.argsort(mass)
        mass = mass[sorted_idx]
        intensities = intensities[sorted_idx]
        snr = snr[sorted_idx]
        bacteria = bacteria[sorted_idx]
        samples = samples[sorted_idx]

    # Group mass/intensities/snr by sample ids
    sample_indices = {i: [] for i in np.unique(samples)}
    for idx, sample in enumerate(samples):
        sample_indices[sample].append(idx)

    # Create adjusted peak list
    for i, peaks in enumerate(peak_list):
        if non_empty[i]:
            indices = sample_indices[i]
            peaks['Mass'] = mass[indices]
            peaks['Intensity'] = intensities[indices]
            peaks['SNR'] = snr[indices]
            peaks['Bacteria'] = bacteria[indices]
    
    return peak_list

def _binPeaks(mass, intensities, samples, tolerance, grouper):
    """
    Binning peaks by splitting at the largest gap.

    Parameters:
    mass (numpy.ndarray): Sorted mass values.
    intensities (numpy.ndarray): Corresponding intensities.
    samples (numpy.ndarray): Corresponding sample id numbers.
    tolerance (float): Maximum deviation of a peak position to be considered as the same peak.
    grouper (function): Grouping function to use.

    Returns:
    numpy.ndarray: Vector of modified mass.
    """
    n = len(mass)
    d = np.diff(mass)

    n_boundaries = max(20, int(np.floor(3 * np.log(n))))
    boundaries = {'left': np.zeros(n_boundaries, dtype=int), 'right': np.zeros(n_boundaries, dtype=int)}

    current_boundary = 0
    boundaries['left'][current_boundary] = 0
    boundaries['right'][current_boundary] = n - 1

    while current_boundary >= 0:
        left = boundaries['left'][current_boundary]
        right = boundaries['right'][current_boundary]
        current_boundary -= 1

        gaps = d[left:right]
        gap_idx = np.argmax(gaps) + left

        # Left side grouping
        l = grouper(mass[left:gap_idx+1], intensities[left:gap_idx+1], samples[left:gap_idx+1], tolerance)
        if l is None:
            current_boundary += 1
            boundaries['left'][current_boundary] = left
            boundaries['right'][current_boundary] = gap_idx
        else:
            mass[left:gap_idx+1] = l

        # Right side grouping
        r = grouper(mass[gap_idx+1:right+1], intensities[gap_idx+1:right+1], samples[gap_idx+1:right+1], tolerance)
        if r is None:
            current_boundary += 1
            boundaries['left'][current_boundary] = gap_idx + 1
            boundaries['right'][current_boundary] = right
        else:
            mass[gap_idx+1:right+1] = r

        # Increase stack size if necessary
        if current_boundary == n_boundaries - 1:
            n_boundaries = int(np.floor(n_boundaries * 1.5))
            boundaries['left'] = np.hstack([boundaries['left'], np.zeros(n_boundaries - len(boundaries['left']))])
            boundaries['right'] = np.hstack([boundaries['right'], np.zeros(n_boundaries - len(boundaries['right']))])

    return mass

# Dummy grouping functions for 'strict', 'relaxed', and 'reference' methods
def grouperStrict(mass, intensities, samples, tolerance):
    # Implement strict grouping logic here
    return mass

def grouperRelaxed(mass, intensities, samples, tolerance):
    # Implement relaxed grouping logic here
    return mass

def grouperRelaxedHighestAtReference(mass, intensities, samples, tolerance):
    # Implement reference grouping logic here
    return mass



def average_by_bacteria(list_dataframes):
    """
    Averages the DataFrames based on the 'patientID' column and returns a list of DataFrames.

    Parameters:
    list_dataframes (list): List of pandas DataFrames with columns 'Mass', 'Intensity', and 'patientID'.

    Returns:
    list: A list of DataFrames, each representing averaged values for a unique patientID.
    """
    # Concatenate all DataFrames into one
    combined_df = pd.concat(list_dataframes, ignore_index=True)

    # Group by 'Bacteria' and calculate the mean for 'Mass' and 'Intensity'
    # averaged_df = combined_df.groupby('patientID').agg({'Mass': 'mean', 'Intensity': 'mean'}).reset_index()
    averaged_df = combined_df.groupby('patientID').agg({'Mass': 'mean', 'Intensity': 'mean'})

    # Create a list of DataFrames for each unique Bacteria
    unique_patientID = averaged_df['patientID'].unique()
    list_of_dfs = [averaged_df[averaged_df['patientID'] == b] for b in unique_patientID]

    return list_of_dfs

def average_by_patient_id(list_dataframes):
    """
    Averages the DataFrames based on the 'PatientId' column and returns a list of DataFrames.

    Parameters:
    list_dataframes (list): List of pandas DataFrames with columns 'Mass', 'Intensity', and 'PatientId'.

    Returns:
    list: A list of DataFrames, each representing averaged values for a unique PatientId.
    """
    # Concatenate all DataFrames into one
    combined_df = pd.concat(list_dataframes, ignore_index=True)

    # Group by 'PatientId' and calculate the mean for 'Mass' and 'Intensity'
    averaged_df = combined_df.groupby('patientID').agg({'Mass': 'mean', 'Intensity': 'mean'}).reset_index()

    # Create a list of DataFrames for each unique PatientId
    unique_patient_ids = averaged_df['patientID'].unique()
    list_of_dfs = [averaged_df[averaged_df['patientID'] == patient_id] for patient_id in unique_patient_ids]

    return list_of_dfs



def average_mass_spectra_objects(spectra_list, method="mean"):
    """
    Averages MassSpectrum objects represented as pandas DataFrames.

    Parameters:
    spectra_list (list): List of pandas DataFrames.
    method (str): Aggregation method ('mean', 'median', 'sum').

    Returns:
    DataFrame: A new DataFrame representing the averaged values.
    """
    # Use the first non-empty spectrum as reference
    non_empty_spectra = [s for s in spectra_list if not s.empty]
    if not non_empty_spectra:
        return pd.DataFrame(columns=['Mass', 'Intensity'])

    # Use the mass values from the first non-empty DataFrame
    mass_values = non_empty_spectra[0]['Mass'].values

    # Interpolate intensities for all DataFrames
    intensity_matrix = []
    for df in spectra_list:
        interp_func = interp1d(df['Mass'], df['Intensity'], bounds_error=False, fill_value=0)
        intensity_values = interp_func(mass_values)
        intensity_matrix.append(intensity_values)

    # Stack intensities and calculate the aggregate
    intensity_array = np.vstack(intensity_matrix)

    if method == 'mean':
        aggregated_intensity = np.nanmean(intensity_array, axis=0)
    elif method == 'median':
        aggregated_intensity = np.nanmedian(intensity_array, axis=0)
    elif method == 'sum':
        aggregated_intensity = np.nansum(intensity_array, axis=0)

    # Create a new DataFrame for the averaged results
    return pd.DataFrame({'Mass': mass_values, 'Intensity': aggregated_intensity})



def average_spectra(dataframes):
    # Group the dataframes in sets of 3
    grouped_dataframes = [dataframes[i:i+3] for i in range(0, len(dataframes), 3)]

    # List to store the averaged dataframes
    averaged_dataframes = []
    
    for group in grouped_dataframes:
        # Retrieve the metadata from the first row of the first dataframe in the group
        metadata = group[0].loc[0, ['patientID', 'patientID.orig', 'experiment', 'loctation', 'Bacteria', 'run']]

        # Concatenate the Mass and Intensity columns across the group
        mass_columns = pd.concat([df['Mass'] for df in group], axis=1)
        intensity_columns = pd.concat([df['Intensity'] for df in group], axis=1)

        # Convert to numeric and interpolate missing values for Mass and Intensity
        mass_columns = mass_columns.apply(pd.to_numeric, errors='coerce').interpolate(method='linear', axis=0, limit_direction='both')
        intensity_columns = intensity_columns.apply(pd.to_numeric, errors='coerce').interpolate(method='linear', axis=0, limit_direction='both')

        # Calculate the mean for Mass and Intensity, ignoring NaNs
        averaged_mass = mass_columns.mean(axis=1)
        averaged_intensity = intensity_columns.mean(axis=1)

        # Create the averaged DataFrame
        averaged_df = pd.DataFrame({
            'Mass': averaged_mass,
            'Intensity': averaged_intensity
        })

        # Add metadata columns by broadcasting the metadata values across all rows
        for col in metadata.index:
            averaged_df[col] = metadata[col]

        # Append the averaged DataFrame to the list
        averaged_dataframes.append(averaged_df)

    # Return the list of averaged DataFrames
    print("Number of averaged dataframes:", len(averaged_dataframes))
    return averaged_dataframes


# new helper to help with debugging
def debug_variable(var, name="Variable"):
    print(f"\n{name} Debug Info")
    print("-" * 30)
    
    # Print type
    print(f"Type: {type(var)}")
    
    # If it's a DataFrame, print shape, columns, index, and a sample
    if isinstance(var, pd.DataFrame):
        print(f"Shape: {var.shape}")
        print(f"Columns: {var.columns}")
        print(f"Index: {var.index}")
        print("Sample Data:\n", var.head())
    
    # If it's a Series, print length, index, and a sample
    elif isinstance(var, pd.Series):
        print(f"Length: {len(var)}")
        print(f"Index: {var.index}")
        print("Sample Data:\n", var.head())
    
    # If it's a list or tuple, print length and a sample of the first few items
    elif isinstance(var, (list, tuple)):
        print(f"Length: {len(var)}")
        print("Sample Data:", var[:5] if len(var) > 5 else var)
    
    # If it's a dictionary, print length and a sample of key-value pairs
    elif isinstance(var, dict):
        print(f"Length: {len(var)}")
        sample_items = list(var.items())[:5]
        print("Sample Data:", sample_items)
    
    # For any other type, just print the value
    else:
        print("Value:", var)
    
    print("-" * 30)


def as_occurrence_list(peaks_list) -> dict:
    """Convert list of DataFrames to occurrence format for filtering.
    
    Args:
        peaks_list: List of DataFrames containing mass spec data
        
    Returns:
        Dictionary containing unique masses and their occurrences across samples
    """
    all_masses = []
    indices = []
    sample_indices = []
    
    for sample_idx, df in enumerate(peaks_list):
        masses = df['Mass'].values
        all_masses.extend(masses)
        indices.extend(range(len(masses)))
        sample_indices.extend([sample_idx] * len(masses))
    
    return {
        'mass': np.array(all_masses),
        'i': np.array(indices),
        'sample': np.array(sample_indices)
    }



def create_whitelist(occurrence_list, 
                    rows, 
                    min_frequency,
                    min_number):
    """Create whitelist for filtering peaks.
    
    Args:
        occurrence_list: Dictionary containing mass occurrences
        rows: List of row indices to consider
        min_frequency: Minimum frequency threshold for peaks
        min_number: Minimum number threshold for peaks
    
    Returns:
        Boolean array indicating which peaks to keep
    """
    if min_frequency is None and min_number is None:
        raise ValueError("min_frequency or min_number must be a meaningful number!")
    
    if min_frequency is not None and min_frequency < 0:
        min_frequency = 0
        print("Warning: min_frequency < 0 does not make sense! Using 0 instead.")
    
    if min_number is not None and min_number < 0:
        min_number = 0
        print("Warning: min_number < 0 does not make sense! Using 0 instead.")
    
    if min_frequency is not None and min_number is not None:
        print("Warning: min_frequency and min_number arguments are given. Choosing the higher one.")
    
    # Calculate minimal number of peaks
    min_peak_number = max(
        min_frequency * len(rows) if min_frequency is not None else float('-inf'),
        min_number if min_number is not None else float('-inf')
    )
    
    # Get samples that are in the specified rows
    mask = np.isin(occurrence_list['sample'], rows)
    selected_indices = occurrence_list['i'][mask]
    
    # Count occurrences of each mass index
    counts = np.bincount(selected_indices, minlength=len(occurrence_list['mass']))
    return counts >= min_peak_number


# def filter_peaks(peaks_list: List[pd.DataFrame],
#                 min_frequency: Optional[float] = None,
#                 min_number: Optional[int] = None,
#                 labels: Optional[Union[List[str], List[int]]] = None,
#                 merge_whitelists: bool = False) -> List[pd.DataFrame]:
def filter_peaks(peaks_list, min_frequency=0.2, min_number=1, labels=None, merge_whitelists=True):
    """Filter peaks which are not frequently represented in different samples.
    
    Args:
        peaks_list: List of DataFrames containing mass spec data
        min_frequency: Minimum frequency threshold for peaks
        min_number: Minimum number threshold for peaks
        labels: Labels for grouping samples
        merge_whitelists: Whether to merge whitelists globally
        
    Returns:
        List of filtered DataFrames
    """
    # Validate input
    if not all(isinstance(df, pd.DataFrame) for df in peaks_list):
        raise TypeError("All elements must be pandas DataFrames")
    
    required_columns = {'Mass', 'Intensity', 'SNR', 'patientID', 'Bacteria'}
    if not all(required_columns.issubset(df.columns) for df in peaks_list):
        raise ValueError(f"All DataFrames must contain columns: {required_columns}")
    
    if labels is None:
        labels = [0] * len(peaks_list)
    
    # Convert labels to categorical if they're not already
    unique_labels = list(dict.fromkeys(labels))  # preserve order
    label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
    labels = [label_to_idx[label] for label in labels]
    
    if len(labels) != len(peaks_list):
        raise ValueError("For each DataFrame there must be a label in labels!")
    
    # Convert to numpy arrays and handle recycling
    n_levels = len(unique_labels)
    min_frequency = np.repeat(
        [min_frequency if min_frequency is not None else np.nan], 
        n_levels
    )
    min_number = np.repeat(
        [min_number if min_number is not None else np.nan], 
        n_levels
    )
    
    # Create occurrence list
    occurrence_list = as_occurrence_list(peaks_list)

    print('occurrence_list')
    debug_variable(occurrence_list)
    print(type(occurrence_list))
    
    # Group indices by labels
    label_indices = [
        [i for i, label in enumerate(labels) if label == level]
        for level in range(n_levels)
    ]
    
    print('label_indices type')
    debug_variable(label_indices)
    print(type(label_indices))


    # Collect whitelists
    whitelists = np.zeros((n_levels, len(occurrence_list['mass'])), dtype=bool)
    print('whitelists')
    debug_variable(whitelists)
    print(type(whitelists))

    print('occurrence_list')
    debug_variable(occurrence_list)
    print(type(occurrence_list))
    
    for i, idx in enumerate(label_indices):
        whitelist = create_whitelist(
            occurrence_list,
            idx,
            min_frequency=min_frequency[i],
            min_number=min_number[i]
        )
        
        if np.any(whitelist):
            if merge_whitelists:
                whitelists = whitelists | whitelist
            else:
                whitelists[i] = whitelist
        else:
            print(f"Warning: Empty peak whitelist for level '{unique_labels[i]}'.")
    
    # Apply whitelists to DataFrames
    filtered_list = []
    for i, df in enumerate(peaks_list):
        label_idx = labels[i]
        sample_mask = occurrence_list['sample'] == i
        peak_indices = occurrence_list['i'][sample_mask]
        wmask = whitelists[label_idx][peak_indices]
        
        # Create filtered DataFrame preserving original index
        filtered_df = df.iloc[wmask].copy()
        filtered_list.append(filtered_df)
    
    return filtered_list


import pandas as pd

# def averageMassSpectra(l, labels, method="mean"):
#     """
#     Averages or sums mass spectra data by given labels.
    
#     Parameters:
#     l (list): List of pandas DataFrames containing mass spectra data.
#     labels (list): List of labels for grouping the DataFrames.
#     method (str): Aggregation method to use, either 'mean', 'median', or 'sum'.
    
#     Returns:
#     pd.DataFrame: DataFrame of aggregated values, grouped by the provided labels.
#     """
#     # Check if method is valid
#     if method not in ["mean", "median", "sum"]:
#         raise ValueError("Method must be one of 'mean', 'median', or 'sum'.")
    
#     # Concatenate the list of DataFrames into one
#     df_combined = pd.concat(l, keys=labels, names=['Label', 'Index'])
    
#     # Group by 'Label' to apply the aggregation method
#     if method == "mean":
#         result = df_combined.groupby('Label').mean()
#     elif method == "median":
#         result = df_combined.groupby('Label').median()
#     elif method == "sum":
#         result = df_combined.groupby('Label').sum()
    
#     return result

# rewriting this to return a list of data frames
# def averageMassSpectra(l, labels, method="mean"):
#     """
#     Averages or sums mass spectra data by given labels.
    
#     Parameters:
#     l (list): List of pandas DataFrames containing mass spectra data.
#     labels (list): List of labels for grouping the DataFrames.
#     method (str): Aggregation method to use, either 'mean', 'median', or 'sum'.
    
#     Returns:
#     pd.DataFrame: DataFrame of aggregated values, grouped by the provided labels.
#     """
#     # Check if method is valid
#     if method not in ["mean", "median", "sum"]:
#         raise ValueError("Method must be one of 'mean', 'median', or 'sum'.")
    
#     # Ensure all elements in the list are DataFrames
#     if not all(isinstance(df, pd.DataFrame) for df in l):
#         raise ValueError("All items in the list must be pandas DataFrames.")
    
#     # Concatenate the list of DataFrames into one
#     df_combined = pd.concat(l, keys=labels, names=['Label', 'Index'])
    
#     # Group by 'Label' to apply the aggregation method
#     if method == "mean":
#         result = df_combined.groupby('Label').mean()
#     elif method == "median":
#         result = df_combined.groupby('Label').median()
#     elif method == "sum":
#         result = df_combined.groupby('Label').sum()
    
#     return result

def averageMassSpectra(l, labels, method="mean"):
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
    if not all(isinstance(df, pd.DataFrame) for df in l):
        raise ValueError("All items in the list must be pandas DataFrames.")
    
    # Concatenate the list of DataFrames into one
    df_combined = pd.concat(l, keys=labels, names=['Mass', 'Intensity'])
    
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
    median = df.median()
    
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

    non_empty = [len(peaks['mass']) != 0 for peaks in peak_list]
    samples = [i for i, peaks in enumerate(peak_list) for _ in range(len(peaks['mass']))]

    # Fetch all mass, intensities, and snr
    mass = np.concatenate([peaks['mass'] for i, peaks in enumerate(peak_list) if non_empty[i]])
    intensities = np.concatenate([peaks['intensity'] for i, peaks in enumerate(peak_list) if non_empty[i]])
    snr = np.concatenate([peaks['snr'] for i, peaks in enumerate(peak_list) if non_empty[i]])

    # Sort values by mass
    sorted_idx = np.argsort(mass)
    mass = mass[sorted_idx]
    intensities = intensities[sorted_idx]
    snr = snr[sorted_idx]
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
        samples = samples[sorted_idx]

    # Group mass/intensities/snr by sample ids
    sample_indices = {i: [] for i in np.unique(samples)}
    for idx, sample in enumerate(samples):
        sample_indices[sample].append(idx)

    # Create adjusted peak list
    for i, peaks in enumerate(peak_list):
        if non_empty[i]:
            indices = sample_indices[i]
            peaks['mass'] = mass[indices]
            peaks['intensity'] = intensities[indices]
            peaks['snr'] = snr[indices]
    
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


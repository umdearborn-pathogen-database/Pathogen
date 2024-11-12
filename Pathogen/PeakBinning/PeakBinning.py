import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

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











##################### NEWEST COMMENT OUT 



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










# New
# def average_mass_spectra(dataframes, labels, method="mean"):
#     """
#     Averages mass spectra based on the given labels.

#     Parameters:
#     dataframes (list): List of pandas DataFrames containing 'Mass', 'Intensity', and other metadata.
#     labels (list): List of labels for grouping the DataFrames.
#     method (str): Aggregation method to use, either 'mean', 'median', or 'sum'.

#     Returns:096cc23c48706e815168951688ecc08f6bbbd063
#     DataFrame: A DataFrame with averaged values for each label.
#     """
#     # Validate input
#     if not isinstance(dataframes, list) or not all(isinstance(df, pd.DataFrame) for df in dataframes):
#         raise ValueError("Input must be a list of pandas DataFrames.")

#     method = method.lower()
#     if method not in ['mean', 'median', 'sum']:
#         raise ValueError("Method must be one of 'mean', 'median', or 'sum'.")

#     # Group DataFrames by labels
#     label_df = pd.DataFrame({'DataFrame': dataframes, 'Labels': labels})

#     # Initialize a list to hold the averaged DataFrames
#     averaged_results = []

#     print("label columns")
#     print(label_df.columns)
#     print("type of label_df")
#     print(type(label_df))

#     for label in label_df['Labels'].unique():
#         # Filter DataFrames for the current label
#         grouped_dfs = label_df[label_df['patientID'] == label]['DataFrame'].tolist()

#         # Average the spectra for this label
#         averaged_df = average_mass_spectra_objects(grouped_dfs, method)
#         averaged_results.append(averaged_df)

#     return averaged_results

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


# # latest average_mass_spectra method
# def average_spectra(dataframes):
#     # Combine all data frames
#     list_df = pd.concat([df for df in dataframes], axis=0, ignore_index=True)
#     list_df = list_df.sort_values(by=['patientID', 'Mass']).reset_index(drop=True)
#     averaged_results = []


#     # Group by `mass`, `bacteria`, and `patientId` to find the average intensity
#     averaged_df = list_df.groupby(['Mass', 'bacteria', 'patientID']).agg({
#         'Intensity': 'mean'
#     }).reset_index()

#     averaged_df = averaged_df.sort_values(by=['patientID', 'Mass']).reset_index(drop=True)

#     return averaged_df

# latest average_mass_spectra method
def average_spectra(dataframes):
    averaged_results = []

    # Process every 3 data frames as a batch
    for i in range(0, len(dataframes), 3):
        # Concatenate the three data frames for the current patient
        combined_df = pd.concat(dataframes[i:i+3], axis=0, ignore_index=True)
        combined_df = combined_df.sort_values(by=['patientID', 'Mass']).reset_index(drop=True)

        # Average the Intensity for each unique Mass value
        averaged_df = combined_df.groupby(['Mass', 'patientID','Bacteria']).agg({
            'Intensity': 'mean'
        }).reset_index()
        
        # Sort the result for consistency
        averaged_df = averaged_df.sort_values(by=['patientID', 'Mass','Bacteria']).reset_index(drop=True)

        # Add the averaged data frame for the current patient to the list
        averaged_results.append(averaged_df)

    return averaged_results  # This will be a list of 35 averaged data frames










    ################################# NEWEST COMMENT OUT 



#     def bin_peaks(dataframes, method='strict', tolerance=0.002):
#     """
#     Binning peaks by splitting at the largest gap.
    
#     Parameters:
#         dataframes (list of pd.DataFrame): List of DataFrames each containing 'Mass', 'Intensity', and 'patientID' columns.
#         method (str): Grouper to use ('strict', 'relaxed', or 'reference').
#         tolerance (float): Maximal deviation of a peak position to be considered as the same peak.
    
#     Returns:
#         list of pd.DataFrame: Adjusted DataFrames after binning.
#     """
#     # Store original mass sample number/id
#     nn = [len(df) for df in dataframes]
#     non_empty = [i for i, count in enumerate(nn) if count > 0]

#     # Fetch all mass, intensities, and patientIDs
#     mass = np.concatenate([df['Mass'].values for df in dataframes if len(df) > 0])
#     intensities = np.concatenate([df['Intensity'].values for df in dataframes if len(df) > 0])
#     samples = np.concatenate([[i] * len(dataframes[i]) for i in non_empty])

#     # Sort values by mass
#     sorted_indices = np.argsort(mass)
#     mass = mass[sorted_indices]
#     intensities = intensities[sorted_indices]
#     samples = samples[sorted_indices]

#     # Select grouper
#     grouper = {
#         "strict": grouper_strict,
#         "relaxed": grouper_relaxed,
#         "reference": grouper_relaxed_highest_at_reference
#     }.get(method, grouper_strict)

#     # Binning
#     mass = bin_peaks_internal(mass, intensities, samples, tolerance, grouper)

#     # Group mass/intensities/samples by sample ids
#     l_idx = {sample_id: np.where(samples == sample_id)[0] for sample_id in np.unique(samples)}

#     # Create adjusted peak list
#     adjusted_dataframes = []
#     for idx in non_empty:
#         peak_indices = l_idx[samples[idx]]
#         adjusted_df = pd.DataFrame({
#             'Mass': mass[peak_indices],
#             'Intensity': intensities[peak_indices],
#             'SNR': None  # SNR needs to be calculated separately
#         })
#         adjusted_dataframes.append(adjusted_df)

#     return adjusted_dataframes


# def bin_peaks_internal(mass, intensities, samples, tolerance, grouper):
#     """
#     Internal function for binning peaks by splitting at the largest gap.
    
#     Parameters:
#         mass (np.ndarray): Sorted array of mass values.
#         intensities (np.ndarray): Corresponding intensities.
#         samples (np.ndarray): Corresponding sample ID numbers.
#         tolerance (float): Maximal deviation of a peak position to be considered as the same peak.
#         grouper (callable): Grouping function.
    
#     Returns:
#         np.ndarray: Modified mass values after binning.
#     """
#     n = len(mass)
#     d = np.diff(mass)

#     # Stack based implementation
#     n_boundaries = max(20, int(3 * np.log(n)))
#     boundary = {'left': np.zeros(n_boundaries, dtype=int), 'right': np.zeros(n_boundaries, dtype=int)}

#     current_boundary = 0
#     boundary['left'][current_boundary] = 0
#     boundary['right'][current_boundary] = n - 1

#     while current_boundary >= 0:
#         left = boundary['left'][current_boundary]
#         right = boundary['right'][current_boundary]
#         current_boundary -= 1
#         gaps = d[left:right]

#         gap_idx = np.argmax(gaps) + left

#         # Left side
#         l = grouper(mass[left:gap_idx + 1], intensities[left:gap_idx + 1], samples[left:gap_idx + 1], tolerance)
#         if np.isnan(l).all():
#             current_boundary += 1
#             boundary['left'][current_boundary] = left
#             boundary['right'][current_boundary] = gap_idx
#         else:
#             mass[left:gap_idx + 1] = l

#         # Right side
#         r = grouper(mass[gap_idx + 1:right + 1], intensities[gap_idx + 1:right + 1], samples[gap_idx + 1:right + 1], tolerance)
#         if np.isnan(r).all():
#             current_boundary += 1
#             boundary['left'][current_boundary] = gap_idx + 1
#             boundary['right'][current_boundary] = right
#         else:
#             mass[gap_idx + 1:right + 1] = r

#         # Increase stack size if needed
#         if current_boundary == n_boundaries - 1:
#             n_boundaries = int(n_boundaries * 1.5)
#             boundary['left'] = np.concatenate([boundary['left'], np.zeros(n_boundaries - current_boundary, dtype=int)])
#             boundary['right'] = np.concatenate([boundary['right'], np.zeros(n_boundaries - current_boundary, dtype=int)])

#     return mass

# # Example placeholder grouper functions
# def grouper_strict(mass, intensities, samples, tolerance):
#     # Implement strict grouping logic
#     return mass  # Placeholder return

# def grouper_relaxed(mass, intensities, samples, tolerance):
#     # Implement relaxed grouping logic
#     return mass  # Placeholder return

# def grouper_relaxed_highest_at_reference(mass, intensities, samples, tolerance):
#     # Implement reference grouping logic
#     return mass  # Placeholder return


################## NEWEST filter_peaks comment out

# def filter_peaks(peaks_list, min_frequency=0.2):
#     """
#     Filters peaks based on a minimum frequency threshold and groups by the patientID column.
    
#     Parameters:
#     - peaks_list: list of DataFrames, each containing peak intensity values and a 'patientID' column.
#     - min_frequency: float, minimum frequency threshold for peak filtering (default is 0.2).
    
#     Returns:
#     - DataFrame with filtered peaks, grouped by patientID, and merged by keeping the maximum intensity per peak.
#     """
#     # Concatenate all DataFrames in the list
#     concatenated_peaks = pd.concat(peaks_list, ignore_index=True)
    
#     # Calculate frequency of occurrence for each peak across all samples
#     peak_presence = (concatenated_peaks.iloc[:, 1:] > 0).mean(axis=1)
    
#     # Filter peaks based on minimum frequency threshold
#     filtered_peaks = concatenated_peaks[peak_presence >= min_frequency]
    
#     # Group by `patientID` and merge peaks by keeping the maximum intensity for each peak
#     merged_peaks = filtered_peaks.groupby('patientID').max().reset_index()

#     return merged_peaks

################## NEWEST filter_peaks comment out

## commenting this out for index issue at the bottom when changing back to data frames
# def filter_peaks(peaks_list, min_frequency=0.2, min_number=1, labels=None, merge_whitelists=False):
#     """
#     Filters peaks which are not frequently represented in different samples.
    
#     Parameters:
#     - peaks_list: list of DataFrames, each containing 'Mass', 'Intensity', 'SNR', and 'patientID' columns.
#     - min_frequency: float, minimal frequency of a peak to be not removed.
#     - min_number: int, minimal (absolute) number of peaks to be not removed.
#     - labels: list or None, labelwise filtering (if None, uses a default).
#     - merge_whitelists: bool, apply whitelists local (False) or global (True).
    
#     Returns:
#     - list of DataFrames with adjusted peaks.
#     """
#     # Test arguments
#     if labels is None:
#         labels = [0] * len(peaks_list)
    
#     # Convert labels to a categorical type to preserve order
#     labels = pd.Series(labels).astype('category')
    
#     # Check that the number of labels matches the number of peak DataFrames
#     if len(labels) != len(peaks_list):
#         raise ValueError("For each item in 'peaks_list', there must be a label in 'labels'!")
    
#     ll = labels.cat.categories
#     nl = len(ll)

#     # Recycle arguments if needed
#     min_frequency = [min_frequency] * nl if isinstance(min_frequency, (int, float)) else min_frequency
#     min_number = [min_number] * nl if isinstance(min_number, (int, float)) else min_number
#     merge_whitelists = bool(merge_whitelists)

#     # Create occurrence list
#     occurrence_list = as_occurrence_list(peaks_list)

#     # Group indices by labels
#     idx = [labels[labels == x].index.tolist() for x in ll]

#     # Collect whitelists
#     w = pd.DataFrame(False, index=range(nl), columns=occurrence_list['mass'])

#     for i in range(nl):
#         wl = whitelist(occurrence_list, idx[i], min_frequency[i], min_number[i])
#         if wl.sum() > 0:
#             if merge_whitelists:
#                 w.iloc[i] = w.iloc[i] | wl
#             else:
#                 w.iloc[i] = w.iloc[i] | wl
#         else:
#             print(f"Warning: Empty peak whitelist for level {ll[i]}.")

#     # Turn matrix back into DataFrames
#     for i in range(nl):
#         for j in idx[i]:
#             mask = w.iloc[i, occurrence_list['sample'] == j]
#             peaks_list[j] = peaks_list[j][mask]
    
#     return peaks_list


# commenting this out and replacing it with tom's filter_peaks method
def filter_peaks(peaks_list, min_frequency=0.2, min_number=1, labels=None, merge_whitelists=True):
    """
    Filters peaks which are not frequently represented in different samples.
    
    Parameters:
    - peaks_list: list of DataFrames, each containing 'Mass', 'Intensity', 'SNR', and 'patientID' columns.
    - min_frequency: float, minimal frequency of a peak to be not removed.
    - min_number: int, minimal (absolute) number of peaks to be not removed.
    - labels: list or None, labelwise filtering (if None, uses a default).
    - merge_whitelists: bool, apply whitelists local (False) or global (True).
    
    Returns:
    - list of DataFrames with adjusted peaks.
    """
    # Test arguments
    if labels is None:
        labels = [0] * len(peaks_list)
    
    # Convert labels to a categorical type to preserve order
    labels = pd.Series(labels).astype('category')
    
    # Check that the number of labels matches the number of peak DataFrames
    if len(labels) != len(peaks_list):
        raise ValueError("For each item in 'peaks_list', there must be a label in 'labels'!")
    
    ll = labels.cat.categories
    nl = len(ll)

    # Recycle arguments if needed
    min_frequency = [min_frequency] * nl if isinstance(min_frequency, (int, float)) else min_frequency
    min_number = [min_number] * nl if isinstance(min_number, (int, float)) else min_number
    merge_whitelists = bool(merge_whitelists)

    # Create occurrence list
    occurrence_list = as_occurrence_list(peaks_list)

    # Group indices by labels
    idx = [labels[labels == x].index.tolist() for x in ll]

    # Collect whitelists
    w = pd.DataFrame(False, index=range(nl), columns=occurrence_list['mass'])

    for i in range(nl):
        wl = whitelist(occurrence_list, idx[i], min_frequency[i], min_number[i])
        if wl.sum() > 0:
            if merge_whitelists:
                w.iloc[i] = w.iloc[i] | wl
            else:
                w.iloc[i] = w.iloc[i] | wl
        else:
            print(f"Warning: Empty peak whitelist for level {ll[i]}.")

    # Turn matrix back into DataFrames
    for i in range(nl):
        for j in idx[i]:
            mask = occurrence_list['sample'] == j  # Create the boolean mask
            # Use mask to select columns in w corresponding to the samples
            peaks_list[j] = peaks_list[j][w.iloc[i][mask].values]  # Use .iloc to select boolean index
    
    return peaks_list

def whitelist(occurrence_list, rows, min_frequency, min_number):
    """
    Helper function to create whitelists for filtering.
    
    Parameters:
    - occurrence_list: DataFrame containing occurrences of peaks.
    - rows: list of indices to be filtered.
    - min_frequency: float, minimal frequency of a peak to be not removed.
    - min_number: int, minimal (absolute) number of peaks to be not removed.
    
    Returns:
    - Series: a boolean Series representing the whitelist.
    """
    if pd.isna(min_frequency) and pd.isna(min_number):
        raise ValueError("Either 'min_frequency' or 'min_number' must be a meaningful number!")
    
    if min_frequency < 0:
        min_frequency = 0
        print("'min_frequency' < 0 does not make sense! Using 0 instead.")
    
    if min_number < 0:
        min_number = 0
        print("'min_number' < 0 does not make sense! Using 0 instead.")

    if not pd.isna(min_frequency) and not pd.isna(min_number):
        print("'min_frequency' and 'min_number' arguments are given. Choosing the higher one.")

    # Calculate minimal number of peaks
    min_peak_number = max(min_frequency * len(rows), min_number)

    # Create whitelist based on the conditions
    return (occurrence_list['sample'].isin(rows).value_counts().reindex(occurrence_list['mass'], fill_value=0) >= min_peak_number)

def as_occurrence_list(peaks_list):
    """
    Creates an occurrence list from the peaks_list.
    
    Parameters:
    - peaks_list: list of DataFrames.
    
    Returns:
    - DataFrame with occurrence information.
    """
    # Initialize an empty DataFrame to hold occurrences
    data = {
        'mass': [],
        'sample': [],
        'i': []
    }
    
    for i, df in enumerate(peaks_list):
        if not df.empty:
            data['mass'].extend(df['Mass'].values)
            data['sample'].extend([i] * len(df))
            data['i'].extend(range(len(df)))

    return pd.DataFrame(data)

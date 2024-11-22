# Imports
import sys
import os

# Necessary for __init__.py classes
# Adds the current file's directory to the system path, allowing the program to locate __init__.py classes from within subdirectories
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Main function
def main():
    from Global import installPackages
    installPackages() # Installs necessary imports for the entirety of the program
    from Global import printWelcomeMsg
    printWelcomeMsg() # Prints the welcome message
    from Global import initializeConfig
    initializeConfig() # Initializes the configuration file
    from Global import database
    database(None, True) # Initializes and checks the database connection
    from Global import getConfigValue
    from Global import printMessage
    
    # Imports after installDependencies()
    import pandas as pd
    import glob
    import scanpy as sc
    sc.settings.verbosity = 3
    sc.settings.set_figure_params(dpi=100, facecolor='white',fontsize=12)
    import matplotlib.pyplot as plt

    printMessage("info", "Importing files...")
    
    # 1. Move Import
    from Global import metaDataFile
    metadata_file = pd.read_csv(metaDataFile)

    # Define the folder path
    from Global import dataDirectory
    folder_path = dataDirectory

    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

    # Load each CSV file into a DataFrame and store in a list
    csv_files.sort()

    # Load each CSV file into a DataFrame, adding a new column for the filename
    dataframes = [
        pd.read_csv(file).assign(Source_File=os.path.splitext(os.path.basename(file))[0])  # Add the filename as a new column
        for file in csv_files
    ]

    #2. Quality Control
    # Check if any DataFrame in the list has null or empty values
    #any_null_or_empty = any(df.isnull().values.any() for df in dataframes) # For future builds
    # Or get a list of which DataFrames contain null or empty values
    #dataframes_with_nulls = [df for df in dataframes if df.isnull().values.any()] # For future builds
    # Calculate the number of rows for each DataFrame
    #row_counts = [len(df) for df in dataframes] # For future builds
    # Create a frequency table of the row counts
    #row_count_table = pd.Series(row_counts).value_counts() # For future builds
    # Check if all DataFrames have regular intervals over the 'Mass' column
    #from QualityControl import is_regular
    #all_regular = all(is_regular(df, 'Mass') for df in dataframes) # For future builds

    printMessage("info", "Trimming the spectra...")

    #3. Transformational Smoothing
    # Define the range to trim and pass the dataframes and range using the pre-processing trim_spectra function
    xl = getConfigValue('options', 'trim-lower-bounds', int)
    xu = getConfigValue('options', 'trim-upper-bounds', int)
    mz_range = (xl, xu)
    from Preprocessing import trim_spectra
    trimmed_spectra_dfs = trim_spectra(dataframes, mz_range)

    printMessage("info", "Implementing baseline correction...")

    #4. Baseline Correction
    # # trimmed_spectra_dfs is a list of trimmed spectra DataFrames
    # # Apply the baseline correction to the first DataFrame
    spectrum_df = trimmed_spectra_dfs
    from BaselineCorrection import apply_snip_baseline_correction    
    trimmed_spectra_baseline_adjusted = apply_snip_baseline_correction(spectrum_df, window_size=10)
    first_trimmed_spectra_baseline_adjusted = trimmed_spectra_baseline_adjusted[0]

    # Opt. Plot Baseline and Original Spectrum
    if(getConfigValue('options', 'plot-baseline', bool) == True):
        printMessage("info", "Plotting the baseline...")
        plt.plot(first_trimmed_spectra_baseline_adjusted['Mass'], first_trimmed_spectra_baseline_adjusted['Intensity'], label='Original Spectrum', color='blue')
        # Plot the baseline
        plt.plot(first_trimmed_spectra_baseline_adjusted['Mass'], first_trimmed_spectra_baseline_adjusted['Baseline'], label='Baseline', color='red', linestyle='--')
        plt.xlabel('m/z')
        plt.ylabel('Intensity')
        plt.title('First Spectrum with Baseline Correction')
        plt.legend()
        plt.show()

    #5. Intensity Calibration
    printMessage("info", "Calibrating intensity...")
    from IntensityCalibration import calibrateIntensity
    trimmed_spectra_baseline_adjusted_calibrated = calibrateIntensity(trimmed_spectra_baseline_adjusted, getConfigValue('options', 'scaling-factor', str))
    
    #6. Spectra Alignment
    printMessage("info", "Aligning the spectra...")
    halfWindowSize = getConfigValue('align-spectra', 'half-window-size', int)
    noiseMethod = getConfigValue('align-spectra', 'noise-method', str)
    snr = getConfigValue('align-spectra', 'SNR', int)
    reference = None
    tolerance = getConfigValue('align-spectra', 'tolerance', float)
    warpingMethod = getConfigValue('align-spectra', 'warping-method', str)
    
    # Align Spectra
    from PeakDetection import align_peaks
    trimmed_spectra_baseline_adjusted_calibrated_aligned = align_peaks(trimmed_spectra_baseline_adjusted_calibrated, half_window_size=halfWindowSize, noise_method=noiseMethod, SNR=snr, reference=reference, tolerance=tolerance, warping_method=warpingMethod)
    
    # Moving this to after the computation - Here - Raw data with meta data
    from Helper import add_run_column_from_patientID
    metadata_file_with_run = add_run_column_from_patientID(metadata_file)

    # Add meta data as additional columns
    from Helper import add_metadata_to_dataframes
    trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged = add_metadata_to_dataframes(trimmed_spectra_baseline_adjusted_calibrated_aligned, metadata_file_with_run)
    
    # Average Mass Spectra
    from PeakBinning import average_spectra
    trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged = average_spectra(trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged)

    # Estimate Noise
    printMessage("info", "Estimating the noise...")
    from PeakBinning import estimateNoise
    noise = estimateNoise(trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged[0])
    first_trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged = trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged[0]

    # Opt. Plot the Noise
    if(getConfigValue('options', 'plot-noise', bool) == True):
        printMessage("info", "Plotting the noise...")
        plt.plot(first_trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged['Mass'], first_trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged['Intensity'], label='Original Spectrum', color='blue')
        plt.plot(noise['Mass'], noise['Intensity'], color='red', label="Noise")
        plt.plot(noise['Mass'], 2 * noise['Intensity'], color='green', label="2 * Noise")
        plt.xlabel('X-axis label')
        plt.ylabel('Y-axis label')
        plt.legend()
        plt.title('Plot of avgSpectra and noise')
        plt.xlabel('m/z')
        plt.ylabel('Intensity')
        plt.title('Spectrum with Noise')
        plt.legend()
        plt.show()

    # Detect Peaks -  https://rdrr.io/cran/MALDIquant/src/R/detectPeaks-methods.R
    printMessage("info", "Detecting peaks...")
    from PeakDetection import detectPeaksInList
    peaks = detectPeaksInList(trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged, SNR=2, half_window_size=20)

    printMessage("info", "Binning peaks...")
    from PeakBinning import binPeaks
    binned_peaks = binPeaks(peaks)

    labels = [df['Bacteria'].values[0] for df in binned_peaks]  # Get the first Bacteria value from each DataFrame
    n = pd.Series(labels).value_counts().shape[0]

    printMessage("info", "FIltering peaks...")
    from PeakBinning import filter_peaks
    # binned_peaks = filter_peaks(binned_peaks, labels=labels)
    binned_peaks = filter_peaks(binned_peaks,min_frequency=0.2,labels=labels,merge_whitelists=True)
    peaks = binned_peaks

    #9. Feature Matrix 
    printMessage("info", "Creating the feature matrix...")
    from FeatureMatrix import intensity_matrix
    featureMatrix = intensity_matrix(peaks,trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged)
    
    #10. SDA - using svd solver to ensure correct data and accuracy
    # Moved below PCA
    
    #11. Distance Matrix - For future builds
    #from scipy.spatial.distance import pdist # For future builds
    #distance_matrix = pdist(featureMatrix, metric='euclidean') # For future builds
    
    #12. Hierarchical Clustering - For future builds
    #from scipy.cluster.hierarchy import linkage # For future builds
    #hClust = linkage(distance_matrix, method='complete') # For future builds
    
    #13. Export Feature Matrix
    if(getConfigValue('options', 'export-feature-matrix-CSV-file', bool) == True):
        printMessage("info", "Exporting Feature Matrix to 'matrix_export.csv...")
        featureMatrix1 = pd.DataFrame(featureMatrix)
        featureMatrix1.to_csv('matrix_export.csv', index=False, header=True)
    
    #14. PCA
    printMessage("info", "Performing Principal Component Analysis...")
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(featureMatrix)
    num_components = getConfigValue('options', 'num-components', int)
    if(not(num_components < n)):
        num_components = n - 1
        printMessage("warn", "Number of components cannot be larger than min(n_features, n_classes - 1), please evaluate your sample size.")
    from Global import initializeTables
    initializeTables(num_components)
    pca = PCA(n_components=num_components)  # number of components to keep per R script
    pca_result = pca.fit_transform(data_scaled)
    
    printMessage("info", "Performing Linear Discriminant Analysis...")
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    lda = LinearDiscriminantAnalysis(solver='svd', n_components=num_components)
    # Commented out for potential use in future builds
    lda.fit(pca_result, labels)
    lda_result = lda.transform(pca_result)
    
    # Add LDA after instead with shrinkage="auto"
    
    if(getConfigValue('options', 'plot-PCA', bool) == True):
        printMessage("info", "Plotting the PCA...")
        plt.scatter(
            pca_result[:, 0],  # First principal component (x-axis)
            pca_result[:, 1],  # Second principal component (y-axis)
            alpha=0.7,         # Transparency to handle overlapping points
            edgecolor='k'      # Optional: Black edges around points for better contrast
        )
        plt.title("PCA Result", fontsize=16)  # Title for context
        plt.xlabel("Principal Component 1", fontsize=14)  # Label for x-axis
        plt.ylabel("Principal Component 2", fontsize=14)  # Label for y-axis
        plt.grid(True) # Add gridlines for better readability
        plt.show()
    
    # Per R script, but not necessary for this, here for potential use in future builds
    # # Perform Hierarchical Clustering on PCA results
    # from sklearn.cluster import AgglomerativeClustering
    # hc = AgglomerativeClustering(n_clusters=2)
    # labels1 = hc.fit_predict(pca_result)
    
    # Opt. Create Dendrogram
    if(getConfigValue('options', 'plot-dendrogram', bool) == True):
        printMessage("info", "Plotting the dendrogram...")
        from scipy.cluster.hierarchy import dendrogram
        from scipy.cluster.hierarchy import linkage # For future builds
        linkage_matrix = linkage(pca_result, method='ward')
        dendrogram(
            linkage_matrix,
            labels=labels,
            leaf_rotation=90,
            leaf_font_size=10
        )
        plt.title("Hierarchical Clustering Dendrogram")
        plt.xlabel("Samples")
        plt.ylabel("Distance")
        plt.show()

    #15. Database - using 'lda_result' as features from PCA
    printMessage("info", "Initiating the database transfer...")
    send_df = pd.DataFrame(lda_result)
    send_df_new_columns = []
    for i in range(num_components):
        send_df_new_columns.append(f'PC{i+1}')
    send_df.columns = send_df_new_columns
    send_df['Bacteria'] = labels
    send_df.insert(0, 'SampleID', labels)
    from Helper import sendValuesToDatabase
    from Helper import getValuesFromDatabase
    returned_df = getValuesFromDatabase(num_components)
    if returned_df is not None:
        send_np = send_df.to_numpy()
        send_np_refined = send_np[:, 1:num_components+1]
        returned_np = returned_df.to_numpy()
        returned_np_refined = returned_np[:, 2:num_components+2]
        matches = []
        from sklearn.metrics.pairwise import cosine_similarity
        for i in range(send_np_refined.shape[0]):
            currentData = send_np_refined[i]
            for j in range(returned_np_refined.shape[0]):
                previousData = returned_np_refined[j]
                currentData = currentData.reshape(1, -1)
                previousData = previousData.reshape(1, -1)
                cs = cosine_similarity(currentData, previousData)
                if cs >= 0.95:
                    matches.append(f"Sample: {send_np[i][0]} matches Database SampleID: {returned_np[j][0]}, Bacteria: {returned_np[j][num_components+1]}, Similarity: {cs[0]}")
        if matches:
            for i in matches:
                printMessage("info", i)
    else:
        printMessage("info", "No matches were found because the table was empty.")
    sendValuesToDatabase(send_df)
if __name__ == "__main__":
    main()
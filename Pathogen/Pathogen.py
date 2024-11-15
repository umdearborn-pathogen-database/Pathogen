# Imports
import sys
import os

# Necessary for __init__.py classes
# Adds the current file's directory to the system path, allowing the program to locate __init__.py classes from within subdirectories
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Main function
def main():
    # Installs necessary imports for the entirety of the program
    from Dependencies.Global import installPackages
    installPackages()
    # Prints the welcome message
    from Dependencies.Global import printWelcomeMsg
    printWelcomeMsg()
    # Initializes the configuration file
    from Dependencies.Global import initializeConfig
    initializeConfig()
    # Initializes and checks the database connection
    from Dependencies.Global import database
    database(None, True)
    from Dependencies.Global import getConfigValue
    
    # Imports after installDependencies()
    import pandas as pd
    import glob
    import os
    import seaborn as sns
    import scanpy as sc
    import scanpy.external as sce
    sc.settings.verbosity = 3
    sc.settings.set_figure_params(dpi=100, facecolor='white',fontsize=12)
    import matplotlib.pyplot as plt
    from Helper.Helper import print_dataframe_summary

    # 1. Move Import
    from Dependencies.Global import metaDataFile
    metadata_file = pd.read_csv(metaDataFile)

    # Define the folder path
    from Dependencies.Global import dataDirectory
    folder_path = dataDirectory

    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

    # Load each CSV file into a DataFrame and store in a list
    csv_files.sort()
    dataframes = [pd.read_csv(file) for file in csv_files]

    # Load each CSV file into a DataFrame, adding a new column for the filename
    dataframes = [
        pd.read_csv(file).assign(Source_File=os.path.splitext(os.path.basename(file))[0])  # Add the filename as a new column
        for file in csv_files
    ]
    # dataframes_with_source_file = [
    #     pd.read_csv(file).assign(Source_File=os.path.splitext(os.path.basename(file))[0])  # Add the filename as a new column
    #     for file in csv_files
    # ]


    #2. Quality Control

    # Check if any DataFrame in the list has null or empty values
    any_null_or_empty = any(df.isnull().values.any() for df in dataframes)

    # Or get a list of which DataFrames contain null or empty values
    dataframes_with_nulls = [df for df in dataframes if df.isnull().values.any()]

    # Calculate the number of rows for each DataFrame
    row_counts = [len(df) for df in dataframes]

    # Create a frequency table of the row counts
    row_count_table = pd.Series(row_counts).value_counts()

    # Check if all DataFrames have regular intervals over the 'Mass' column
    from QualityControl.QualityControl import is_regular
    all_regular = all(is_regular(df, 'Mass') for df in dataframes)

    #3. Transformational Smoothing
    # Define the range to trim and pass the dataframes and range using the pre-processing trim_spectra function
    xl = getConfigValue('options', 'trim-lower-bounds', int)
    xu = getConfigValue('options', 'trim-upper-bounds', int)
    mz_range = (xl, xu)
    from Preprocessing.Preprocessing import trim_spectra
    trimmed_spectra_dfs = trim_spectra(dataframes, mz_range)


    #4. Baseline Correction
    # # trimmed_spectra_dfs is a list of trimmed spectra DataFrames
    # # Apply the baseline correction to the first DataFrame
    spectrum_df = trimmed_spectra_dfs
    first_spectrum_df = trimmed_spectra_dfs[0]

    # Apply the SNIP baseline correction
    from BaselineCorrection.BaselineCorrection import apply_snip_baseline_correction    
    trimmed_spectra_baseline_adjusted = apply_snip_baseline_correction(spectrum_df, window_size=10)
    first_trimmed_spectra_baseline_adjusted = trimmed_spectra_baseline_adjusted[0]

    # plt.plot(x, y, label='Original data')
    # Assuming 'spectrum_df' is your DataFrame with 'm/z', 'intensity', and 'baseline' columns
    # Plot the original spectrum
    plt.plot(first_trimmed_spectra_baseline_adjusted['Mass'], first_trimmed_spectra_baseline_adjusted['Intensity'], label='Original Spectrum', color='blue')

    # Plot the baseline
    plt.plot(first_trimmed_spectra_baseline_adjusted['Mass'], first_trimmed_spectra_baseline_adjusted['Baseline'], label='Baseline', color='red', linestyle='--')

    # Add labels and title
    plt.xlabel('m/z')
    plt.ylabel('Intensity')
    plt.title('First Spectrum with Baseline Correction')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()


    #5. Intensity Calibration
    from IntensityCalibration.IntensityCalibration import calibrateIntensity
    trimmed_spectra_baseline_adjusted_calibrated = calibrateIntensity(trimmed_spectra_baseline_adjusted, getConfigValue('options', 'scaling-factor', str))
    
    #6. Spectra Alignment
    halfWindowSize = getConfigValue('align-spectra', 'half-window-size', int)
    noiseMethod = getConfigValue('align-spectra', 'noise-method', str)
    snr = getConfigValue('align-spectra', 'SNR', int)
    reference = None
    tolerance = getConfigValue('align-spectra', 'tolerance', float)
    warpingMethod = getConfigValue('align-spectra', 'warping-method', str)
    allowNoMatches = getConfigValue('align-spectra', 'allow-no-matches', bool)
    emptyNoMatches = getConfigValue('align-spectra', 'empty-no-matches', bool)
    
    # Align Spectra
    from PeakDetection.PeakDetection import align_peaks
    trimmed_spectra_baseline_adjusted_calibrated_aligned = align_peaks(trimmed_spectra_baseline_adjusted_calibrated, half_window_size=20, noise_method="MAD", SNR=2, reference=None, tolerance=0.002, warping_method="lowess")
    
    # Moving this to after the computation - Here - Raw data with meta data
    from Helper.Helper import add_run_column_from_patientID
    metadata_file_with_run = add_run_column_from_patientID(metadata_file)

    # Add meta data as additional columns
    from Helper.Helper import add_metadata_to_dataframes
    trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged = add_metadata_to_dataframes(trimmed_spectra_baseline_adjusted_calibrated_aligned, metadata_file_with_run)
    

    # Average Mass Spectra
    from PeakBinning.PeakBinning import average_spectra
    trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged = average_spectra(trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged)

    # Estimate Noise
    from PeakBinning.PeakBinning import estimateNoise
    noise = estimateNoise(trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged[0])
    first_trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged = trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged[0]

    # Print the noise
    # Assuming 'trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged' is your DataFrame with 'm/z', 'intensity', and 'baseline' columns
    # Plot the original spectrum
    plt.plot(first_trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged['Mass'], first_trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged['Intensity'], label='Original Spectrum', color='blue')

    # Plot the noise data
    plt.plot(noise['Mass'], noise['Intensity'], color='red', label="Noise")

    plt.plot(noise['Mass'], 2 * noise['Intensity'], color='green', label="2 * Noise")

    # Add labels, legend, and title if needed
    plt.xlabel('X-axis label')
    plt.ylabel('Y-axis label')
    plt.legend()
    plt.title('Plot of avgSpectra and noise')

    # Add labels and title
    plt.xlabel('m/z')
    plt.ylabel('Intensity')
    plt.title('Spectrum with Noise')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()

    # Detect Peaks -  https://rdrr.io/cran/MALDIquant/src/R/detectPeaks-methods.R
    from PeakDetection.PeakDetection import detectPeaksInList
    peaks = detectPeaksInList(trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged, SNR=2, half_window_size=20)

    from PeakBinning.PeakBinning import binPeaks
    binned_peaks = binPeaks(peaks)


    labels = [df['Bacteria'].values[0] for df in binned_peaks]  # Get the first Bacteria value from each DataFrame

    from PeakBinning.PeakBinning import filter_peaks
    # binned_peaks = filter_peaks(binned_peaks, labels=labels)
    binned_peaks = filter_peaks(binned_peaks,min_frequency=0.2,labels=labels,merge_whitelists=True)
    peaks = binned_peaks


    #9. Feature Matrix 
    from FeatureMatrix.FeatureMatrix import intensity_matrix
    featureMatrix = intensity_matrix(peaks,trimmed_spectra_baseline_adjusted_calibrated_aligned_metadata_merged_averaged)
    featureMatrixCopy = featureMatrix

# Debug from here

    #10. SDA
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    lda = LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto')
    lda.fit(featureMatrix, labels)
    
    #11. Distance Matrix
    from scipy.spatial.distance import pdist
    distance_matrix = pdist(featureMatrix, metric='euclidean')
    
    #12. Hierarchical Clustering
    from scipy.cluster.hierarchy import linkage
    hClust = linkage(distance_matrix, method='complete')
    
    #13. Export Feature Matrix
    featureMatrix.to_csv('matrix_export.csv', index=False, header=True)
    
    #14. PCA
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(featureMatrix)

    pca = PCA(n_components=2)  # number of components to keep per R script
    pca_result = pca.fit_transform(data_scaled)
    
    gr = pd.Categorical(featureMatrix.iloc[:, 0], categories=labels)

    # If you want the result as a pandas Series
    gr = pd.Series(gr)
    print(gr)
    
    # Opt. Perform Hierarchical Clustering on PCA results
    from sklearn.cluster import AgglomerativeClustering
    hc = AgglomerativeClustering(n_clusters=2)
    labels = hc.fit_predict(pca_result)
    
    # Opt. Create Dendrogram
    from scipy.cluster.hierarchy import dendrogram
    linkage_matrix = linkage(pca_result, method='ward')
    dendrogram(linkage_matrix)
    plt.title("Hierarchical Clustering Dendrogram")
    plt.xlabel("Samples")
    plt.ylabel("Distance")
    plt.show()
    
    # going to review this last bit with Darrell tomorrow
    # rownames(featureMatrix) <- avgSpectra.info$patientID
    # Xtrain <- featureMatrix
    # Ytrain <- avgSpectra.info$Bacteria
    # ddar <- sda.ranking(Xtrain=featureMatrix, L=Ytrain, fdr=FALSE,diagonal=TRUE)
    # distanceMatrix <- dist(featureMatrix, method="euclidean")
    # hClust <- hclust(distanceMatrix, method="complete")
    # plot(hClust, hang=-1)
    # write.csv(featureMatrix, file = "PCA1.csv")
    # z <- read.csv(file = 'PCA1.csv', header = TRUE)



    # pca <- prcomp(z[,-1], scale.=TRUE)
    # gr <- factor(z[,1], labels=avgSpectra.info$Bacteria)
    # summary(gr)
    
    # Break
    
    # pca2d(pca, group=gr, legend="topleft")
    # pca3d(pca, group=gr, show.ellipses=TRUE, ellipse.ci=0.75, show.plane=FALSE, legend="topleft")

    # res.pca <- PCA(featureMatrix, scale.unit=TRUE, ncp=2,graph = FALSE)
    # res.hcpc <- HCPC(res.pca, graph = FALSE)
    # fviz_dend(res.hcpc,cex = 0.55, palette = "jco", rect = TRUE, rect_fill = FALSE, rect_border = "jco", labels_track_height = 300.0,H =0.5)

    # Database

if __name__ == "__main__":
    main()


# Useful links
# https://pandas.pydata.org/docs/user_guide/style.html
# https://github.com/sgibb/MALDIquant/blob/master/R/alignSpectra-functions.R

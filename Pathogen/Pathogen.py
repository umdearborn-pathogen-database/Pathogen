# Imports for packages already included with Python
import sys
import os
# Necessary for __init__.py classes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Helper.Helper import print_dataframe_summary
from Dependencies.Global import getConfigValue

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

    # 1. Move Import
    metadata_file = pd.read_csv('Data/Import/info-ecoli-MAI.csv')

    # Debugging
    #    print(metadata_file.head())

    # Optional: commented out in R file    
        # spectra_file = pd.read_csv('MAI-redo-ecoli.csv')

    # Define the folder path
    folder_path = 'Data/Import/MAI-redo-ecoli'

    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

    # Load each CSV file into a DataFrame and store in a list
    dataframes = [pd.read_csv(file) for file in csv_files]


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

    # Debugging - Prints some visuals of the dataframe
    print("Object characteristics")
    print(print_dataframe_summary(trimmed_spectra_dfs))


    #4. Baseline Correction

    # going to use this for now
    # trimmed_spectra_dfs is a list of trimmed spectra DataFrames
    # Apply the baseline correction to the first DataFrame
    # spectrum_df = trimmed_spectra_dfs[0]

    # # Assuming the signal is in a column named Intensity
    # signal = spectrum_df['Intensity'].values

    # # Apply the SNIP baseline correction
    # from BaselineCorrection.BaselineCorrection import snip_baseline_correction
    # baseline = snip_baseline_correction(signal, iterations=150)

    # # Optionally: Add the baseline as a new column to your DataFrame
    # spectrum_df['Baseline'] = baseline

    # # Now you can subtract the baseline from the signal if needed
    # corrected_signal = signal - baseline
    # # spectrum_df['Corrected_Intensity'] = corrected_signal
    # spectrum_df['Corrected_Intensity'] = corrected_signal

    # # Assuming 'spectrum_df' is your DataFrame with 'm/z', 'intensity', and 'baseline' columns

    # # Plot the original spectrum
    # plt.plot(spectrum_df['Mass'], spectrum_df['Intensity'], label='Original Spectrum', color='blue')

    # # Plot the baseline
    # plt.plot(spectrum_df['Mass'], spectrum_df['Baseline'], label='Baseline', color='red', linestyle='--')

    # # Optionally: Plot the original spectrum minus the baseline
    # # plt.plot(spectrum_df['Mass'], spectrum_df['Corrected_Intensity'], label='Corrected Spectrum', color='green')

    # # Add labels and title
    # plt.xlabel('m/z')
    # plt.ylabel('Intensity')
    # plt.title('Spectrum with Baseline Correction')

    # # Add a legend
    # plt.legend()

    # # Show the plot
    # plt.show()


    
    # # trimmed_spectra_dfs is a list of trimmed spectra DataFrames
    # # Apply the baseline correction to the first DataFrame
    spectrum_df = trimmed_spectra_dfs
    print("list spectra")
    print(type(spectrum_df))
    print(spectrum_df[0].head())
    first_spectrum_df = trimmed_spectra_dfs[0]
    print("first spectra")
    print(type(first_spectrum_df))
    print(first_spectrum_df.head())
    # get just the intensity values from the list of data frames
    # signal = [df[['Intensity']] for df in spectrum_df]

    # Apply the SNIP baseline correction
    from BaselineCorrection.BaselineCorrection import snip_baseline_correction
    baseline = snip_baseline_correction([first_spectrum_df], iterations=50)
    print("returned first spectra")
    print(type(baseline))
    print(baseline[0].head())
    first_spectrum_df['Baseline'] = baseline[0]['Baseline']

    # Optionally: Add the baseline as a new column to your DataFrame
    # spectrum_df['Baseline'] = baseline

    # Now you can subtract the baseline from the signal if needed
    # corrected_intensity = signal - baseline
    # spectrum_df['Corrected_Intensity'] = corrected_signal
    # spectrum_df['Intensity'] = corrected_signal

    # Assuming 'spectrum_df' is your DataFrame with 'm/z', 'intensity', and 'baseline' columns

    # Plot the original spectrum
    plt.plot(first_spectrum_df['Mass'], first_spectrum_df['Intensity'], label='Original Spectrum', color='blue')

    # Plot the baseline
    plt.plot(first_spectrum_df['Mass'], first_spectrum_df['Baseline'], label='Baseline', color='red', linestyle='--')

    # Optionally: Plot the original spectrum minus the baseline
    # plt.plot(spectrum_df['Mass'], spectrum_df['Corrected_Intensity'], label='Corrected Spectrum', color='green')

    # Add labels and title
    plt.xlabel('m/z')
    plt.ylabel('Intensity')
    plt.title('First Spectrum with Baseline Correction')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()

    # Finish removing baseline from the entire the dataframe list
    trimmed_spectra_baseline_adjusted = snip_baseline_correction(spectrum_df, iterations=50)
    print("Object characteristics After Baseline Removal")
    print(print_dataframe_summary(trimmed_spectra_baseline_adjusted))
    # trimmed_spectra_baseline_adjusted['Baseline'] = trimmed_spectra_baseline_adjusted[0]['Baseline']
    
    # replot that to test
    # Plot the original spectrum
    second_specturm_df_baseline_adjusted = trimmed_spectra_baseline_adjusted[1]
    plt.plot(second_specturm_df_baseline_adjusted['Mass'], second_specturm_df_baseline_adjusted['Intensity'], label='Original Spectrum', color='blue')

    # Plot the baseline
    plt.plot(second_specturm_df_baseline_adjusted['Mass'], second_specturm_df_baseline_adjusted['Baseline'], label='Baseline', color='red', linestyle='--')

        # Add labels and title
    plt.xlabel('m/z')
    plt.ylabel('Intensity')
    plt.title('Second Spectrum with Baseline Correction')

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
    from PeakDetection.PeakDetection import alignSpectra
    trimmed_spectra_baseline_adjusted_calibrated_aligned = alignSpectra(trimmed_spectra_baseline_adjusted_calibrated, halfWindowSize, noiseMethod, snr, reference, tolerance, warpingMethod, allowNoMatches, emptyNoMatches)
    
    # Average Mass Spectra
    from PeakBinning.PeakBinning import averageMassSpectra
    trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged = averageMassSpectra(trimmed_spectra_baseline_adjusted_calibrated_aligned, metadata_file['patientID'].unique())
    trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged.attrs = metadata_file['patientID'].unique()
    print_dataframe_summary(trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged)

    # Estimate Noise
    from PeakBinning.PeakBinning import estimateNoise
    noise = estimateNoise(trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged[0])

    # Print the noise
    # Assuming 'trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged' is your DataFrame with 'm/z', 'intensity', and 'baseline' columns
    # Plot the original spectrum
    plt.plot(trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged['Mass'], trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged['Intensity'], label='Original Spectrum', color='blue')

    # Plot the noise data
    plt.plot(noise[:, 0], noise[:, 1], color='red', label="SNR == 1")

    # Plot 2 * noise[:, 1] in blue
    plt.plot(noise[:, 0], 2 * noise[:, 1], color='blue', label="2 * Noise")

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

    # Detect Peaks 
    from PeakDetection.PeakDetection import detectPeaks
    peaks = detectPeaks(trimmed_spectra_baseline_adjuted_calibrated_aligned_averaged, SNR=2, halfWindowSize=20)

    from PeakBinning.PeakBinning import binPeaks
    binned_peaks = binPeaks(peaks)

    # data to save to SQL
    # save raw data / trimmed (at which point? ask Darrell)
    # columns = id, mass, intensity, created on date
    # save feature matrix
    # columns = id,
    # save output of pca
    
    # remaining R code
    # peaks <- binPeaks(peaks)
    # peaks <- filterPeaks(peaks, minFrequency=c(0.2),labels=avgSpectra.info$Bacteria, mergeWhitelists=TRUE)
    # featureMatrix <- intensityMatrix(peaks, avgSpectra)
    # #exclude varibles
    # #featureMatrix <- featureMatrix[,-c(726:730)]

    # rownames(featureMatrix) <- avgSpectra.info$patientID
    # Xtrain <- featureMatrix
    # Ytrain <- avgSpectra.info$Bacteria
    # ddar <- sda.ranking(Xtrain=featureMatrix, L=Ytrain, fdrs=FALSE,diagonal=TRUE)
    # distanceMatrix <- dist(featureMatrix, method="euclidean")
    # hClust <- hclust(distanceMatrix, method="complete")
    # plot(hClust, hang=-1)
    # write.csv(featureMatrix, file = "PCA1.csv")
    # z <- read.csv(file = 'PCA1.csv', header = TRUE)



    # pca <- prcomp(z[,-1], scale.=TRUE)
    # gr <- factor(z[,1], labels=avgSpectra.info$Bacteria)
    # summary(gr)
        


if __name__ == "__main__":
    main()

#6. Spectra Alignment

#7. Peak Detection

#8. Peak Binning

#9. Feature Matrix


# Useful links
# https://pandas.pydata.org/docs/user_guide/style.html
# https://github.com/sgibb/MALDIquant/blob/master/R/alignSpectra-functions.R


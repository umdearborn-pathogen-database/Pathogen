# Imports for packages already included with Python
import sys
import os
# Necessary for __init__.py classes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Dependencies.Setup import installDependencies
from ConfigurationFile.Config import initializeConfig
from ConfigurationFile.Config import getConfigValueCasted
from QualityControl.QualityControl import is_regular
from Preprocessing.Preprocessing import trim_spectra
from BaselineCorrection.BaselineCorrection import snip_baseline_correction
from IntensityCalibration.IntensityCalibration import calibrateIntensity
from PeakDetection.PeakDetection import alignSpectra

# Main function
def main():
    initializeConfig()
    from DatabaseConnection.DatabaseConnector import initializeDatabase
    initializeDatabase()
    installDependencies()
    # Imports after installDependencies()
    import pandas as pd
    import glob
    import os
    import seaborn as sns
    import MALDIpy
    import scanpy as sc
    import scanpy.external as sce
    sc.settings.verbosity = 3
    sc.settings.set_figure_params(dpi=100, facecolor='white',fontsize=12)
    import matplotlib.pyplot as plt

    # 1. Move Import
    print("successfully installed dependencies!")
    metadata_file = pd.read_csv('Data/Import/info-ecoli-MAI.csv')
    print(metadata_file.head())
    # spectra_file = pd.read_csv('MAI-redo-ecoli.csv')

    # Define the folder path
    folder_path = 'Data/Import/MAI-redo-ecoli'

    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

    # Load each CSV file into a DataFrame and store in a list
    dataframes = [pd.read_csv(file) for file in csv_files]

    # Print the head of the first DataFrame
    print(dataframes[0].head())


    #2. Quality Control

    # Check if any DataFrame in the list has null or empty values
    any_null_or_empty = any(df.isnull().values.any() for df in dataframes)

    # Or get a list of which DataFrames contain null or empty values
    dataframes_with_nulls = [df for df in dataframes if df.isnull().values.any()]

    if any_null_or_empty:
        print("At least one DataFrame contains null or empty values.")
    else:
        print("No DataFrames contain null or empty values.")
    
    print('Dataframes with nulls')
    print(dataframes_with_nulls)

    # Calculate the number of rows for each DataFrame
    row_counts = [len(df) for df in dataframes]

    # Create a frequency table of the row counts
    row_count_table = pd.Series(row_counts).value_counts()

    print('Row_Count_Table')
    print(row_count_table)
    print('count of dataframes/csvs')
    print(dataframes.count)

    # Check if all DataFrames have regular intervals over the 'Mass' column
    all_regular = all(is_regular(df, 'Mass') for df in dataframes)

    if all_regular:
        print("All DataFrames have regular intervals.")
    else:
        print("Not all DataFrames have regular intervals.")


    #3. Transformational Smoothing

    # Define the range to trim and pass the dataframes and range using the pre-processing trim_spectra function
    xl = getConfigValueCasted('options', 'trim-lower-bounds', int)
    xu = getConfigValueCasted('options', 'trim-upper-bounds', int)
    mz_range = (xl, xu)
    trimmed_spectra_dfs = trim_spectra(dataframes, mz_range)
    print("The Trimmed Spectra")
    print(trimmed_spectra_dfs[0].head())


    #4. Baseline Correction

    # trimmed_spectra_dfs is a list of trimmed spectra DataFrames
    # Apply the baseline correction to the first DataFrame
    spectrum_df = trimmed_spectra_dfs[0]  

    # Assuming the signal is in a column named Intensity
    signal = spectrum_df['Intensity'].values

    # Apply the SNIP baseline correction
    baseline = snip_baseline_correction(signal, iterations=150)

    # Optionally: Add the baseline as a new column to your DataFrame
    spectrum_df['Baseline'] = baseline

    # Now you can subtract the baseline from the signal if needed
    corrected_signal = signal - baseline
    spectrum_df['Corrected_Intensity'] = corrected_signal


    # Assuming 'spectrum_df' is your DataFrame with 'm/z', 'intensity', and 'baseline' columns

    # Plot the original spectrum
    plt.plot(spectrum_df['Mass'], spectrum_df['Intensity'], label='Original Spectrum', color='blue')

    # Plot the baseline
    plt.plot(spectrum_df['Mass'], spectrum_df['Baseline'], label='Baseline', color='red', linestyle='--')

    # Optionally: Plot the original spectrum minus the baseline
    # plt.plot(spectrum_df['Mass'], spectrum_df['Corrected_Intensity'], label='Corrected Spectrum', color='green')

    # Add labels and title
    plt.xlabel('m/z')
    plt.ylabel('Intensity')
    plt.title('Spectrum with Baseline Correction')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()

    #5. Intensity Calibration
    spectrum_df = calibrateIntensity(spectrum_df, getConfigValueCasted('options', 'scaling-factor', str))
    
    #6. Spectra Alignment
    spectrum_df = alignSpectra(spectrum_df)


if __name__ == "__main__":
    main()

#6. Spectra Alignment

#7. Peak Detection

#8. Peak Binning

#9. Feature Matrix
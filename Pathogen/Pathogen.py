# Imports for packages already included with Python
import sys
import os
# Necessary for __init__.py classes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the loadConfig method from Dependencies/Setup.py
from Dependencies.Setup import loadConfig
# Import the install method from Dependencies/Setup.py
from Dependencies.Setup import install
# Import the install function from Dependencies/Setup.py
from Dependencies.Setup import installDependencies
# Import the getConfigValue function from Dependencies/Setup.py
from Dependencies.Setup import getConfigValue

# Main function
def main():
    loadConfig()
    # Pulling dependencies defined in Dependencies/Setup.py
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
    print("successfully installed dependencies!")

    metadata_file = pd.read_csv('Data/Import/info-ecoli-MAI.csv')
    print(metadata_file.head())
    # spectra_file = pd.read_csv('MAI-redo-ecoli.csv')

    # Define the folder path
    # folder_path = 'Data/Import/MAI-redo-ecoli/'
    folder_path = 'Data/Import/MAI-redo-ecoli'

    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

    # Load each CSV file into a DataFrame and store in a list
    dataframes = [pd.read_csv(file) for file in csv_files]

    # Print the head of the first DataFrame
    print(dataframes[0].head())

    if(getConfigValue('options', 'remove-null-valued-spectra') == 'true'):
        ###
        print("This is for removing with removeNullValuedSpectra()")


    if(getConfigValue('options', 'cancel-if-sum-is-zero') == 'true'):
        ###
        print("This is for checking to ensure that the sum of the intensities are not zero")


if __name__ == "__main__":
    main()

# 1. Move Import
# Open the file in read mode
# with open('Pathogen/TestData/air.POSITIVE.txt', 'r') as file:
#     # Read the contents of the file
#     contents = file.read()

# Print the contents
# print(contents)

#2. Quality Control

#3. Transormational Smoothing

#4. Baseline Correction

#5. Intensity Calibration

#6. Spectra Alignment

#7. Peak Detection

#8. Peak Binning

#9. Feature Matrix
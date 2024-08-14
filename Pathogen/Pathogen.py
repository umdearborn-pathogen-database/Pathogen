# Imports for packages already included with Python
import sys
import os
# Necessary for __init__.py classes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the install method from the Dependencies/Setup.py
from Dependencies.Setup import install
# Import the install function from the Dependencies/Setup.py
from Dependencies.Setup import installDependencies

# Main function
def main():
    # Pulling dependencies defined in Dependencies/Setup.py
    installDependencies()
    # Imports after installDependencies()
    import pandas as pd
    import seaborn
    import MALDIpy

    # ~Testing~
    print("successfully installed dependencies!")
    # ~End Testing~

    raw_file = pd.read_csv('Data/Import/info-ecoli-MAI.csv')

    # ~Testing~
    print(raw_file.head())
    # ~End Testing~

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
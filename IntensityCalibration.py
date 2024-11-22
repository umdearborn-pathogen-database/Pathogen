import numpy as np
from Global import printMessage

def calibrateIntensity(spectra_list, method):
    calibrated_dataframes = []  # List to hold calibrated DataFrames

    for spectrum in spectra_list:
        if method == "TIC":
            scalingFactor = totalIonCurrent(spectrum)
            spectrum['Intensity'] /= scalingFactor
            calibrated_dataframes.append(spectrum)

        elif method == "PQN":
            tic = totalIonCurrent(spectrum)
            normalized_intensity = spectrum['Intensity'] / tic
            reference_intensity = np.median(spectrum['Intensity'])
            quotients = normalized_intensity / reference_intensity
            median_quotient = np.median(quotients)
            spectrum['Intensity'] /= median_quotient
            calibrated_dataframes.append(spectrum)

        elif method == "median":
            scalingFactor = medianScalingFactor(spectrum)
            spectrum['Intensity'] /= scalingFactor
            calibrated_dataframes.append(spectrum)

        else:
            printMessage("err", "Issue calibrating intensity. Method is incorrectly defined.")
            # Optionally, you could return the already calibrated dataframes so far
            return calibrated_dataframes

    return calibrated_dataframes  # Return the list of calibrated DataFrames
    
def totalIonCurrent(spectrum):
    intensities = spectrum['Intensity'].values
    masses = spectrum['Mass'].values
    left = intensities[:-1].astype(np.float64)
    right = intensities[1:].astype(np.float64)
    massDiff = np.diff(masses).astype(np.float64)
    return np.sum(((left + right) / 2.0) * massDiff)

def medianScalingFactor(spectrum):
    return np.median(spectrum['Intensity'])
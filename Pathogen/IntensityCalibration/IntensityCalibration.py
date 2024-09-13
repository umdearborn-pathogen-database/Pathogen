import numpy as np

# Logging
from ConfigurationFile.Config import log

def calibrateIntensity(spectrum, method):
    if(method == "TIC"):
        scalingFactor = totalIonCurrent(spectrum)
        spectrum['Intensity'] /= scalingFactor
        return spectrum
    elif(method == "PQN"):
        tic = totalIonCurrent(spectrum)
        normalized_intensity = spectrum['Intensity'] / tic
        reference_intensity = np.median(spectrum['Intensity'])
        quotients = normalized_intensity / reference_intensity
        median_quotient = np.median(quotients)
        spectrum['Intensity'] /= median_quotient
        return spectrum
    elif(method == "median"):
        scalingFactor = medianScalingFactor(spectrum)
        spectrum['Intensity'] /= scalingFactor
        return spectrum
    else:
        log("Error calibrating intensity. Method is incorrectly defined.")

def totalIonCurrent(spectrum):
    intensities = spectrum['Intensity'].values
    masses = spectrum['Intensity'].values
    left = intensities[:-1].astype(np.float64)
    right = intensities[1:].astype(np.float64)
    massDiff = np.diff(masses).astype(np.float64)
    return np.sum(((left + right) / 2.0) * massDiff)

def medianScalingFactor(spectrum):
    return np.median(spectrum['Intensity'])
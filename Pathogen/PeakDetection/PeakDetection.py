import numpy as np
from scipy.signal import find_peaks
import statsmodels.api as sm

from Helper.Helper import print_dataframe_summary
from Pathogen.Dependencies.Global import printMessage

def alignSpectra(spectra, halfWindowSize=20, noiseMethod="MAD", SNR=2, reference=None, tolerance=0.002, warpingMethod="lowess", allowNoMatches=False, emptyNoMatches=False, **kwargs):
    peaks = detectPeaks(spectra, halfWindowSize=halfWindowSize, noiseMethod=noiseMethod, SNR=SNR)
    warpingFunctions = []
    x = peaks['Mass']
    d = np.zeros_like(x)
    if warpingMethod == "lowess":
        wf = warpingFunctionLowess(x, d, **kwargs)
    elif warpingMethod == "linear":
        wf = warpingFunctionLinear(x, d, **kwargs)
    elif warpingMethod == "quadratic":
        wf = warpingFunctionQuadratic(x, d, **kwargs)
    elif warpingMethod == "cubic":
        wf = warpingFunctionCubic(x, d, **kwargs)
    else:
        printMessage("err", f"Unknown warping method: {warpingMethod}")
        wf = None
    warpingFunctions.append(wf)
    alignedSpectra = warpMassSpectra(spectra, warpingFunctions, emptyNoMatches=emptyNoMatches)
    return alignedSpectra

# def align_spectra(spectrum, target_mass_range):
#     """Aligns the spectrum to a common mass range using interpolation."""
#     common_mass = np.linspace(target_mass_range[0], target_mass_range[1], num=1000)

#     # Ensure spectrum is a DataFrame
#     if isinstance(spectrum, pd.DataFrame):
#         masses = spectrum['Mass'].to_numpy()  # Access mass column
#         intensities = spectrum['Intensity'].to_numpy()  # Access intensity column

#         # Create interpolation function
#         interp_func = interp1d(masses, intensities, bounds_error=False, fill_value=0)

#         # Interpolate intensity values onto the common mass grid
#         aligned_intensity = interp_func(common_mass)

#         # Return the aligned spectrum as a DataFrame
#         return pd.DataFrame({'Mass': common_mass, 'Intensity': aligned_intensity})
#     else:
#         raise ValueError("Input spectrum is not a valid DataFrame.")


def detectPeaks(spectra, halfWindowSize=20, noiseMethod="MAD", SNR=2):
    # mass = spectrum_df['mass'].values
    # intensity = spectrum_df['intensity'].values

    intensity = spectra['Intensity'].values
    mass = spectra['Mass'].values
    peakIndices, _ = find_peaks(intensity, distance=halfWindowSize)
    return {'Mass': mass[peakIndices], 'Intensity': intensity[peakIndices]}

def warpingFunctionLowess(x, d, **kwargs):
    lowess = sm.nonparametric.lowess(d, x, **kwargs)
    if lowess.ndim != 2 or lowess.shape[1] != 2:
        printMessage("err", ValueError("Lowess result is not a 2D array with two columns."))
    return lowess

def warpingFunctionLinear(x, d, **kwargs):
    coeffs = np.polyfit(x, d, 1)
    return np.poly1d(coeffs)

def warpingFunctionQuadratic(x, d, **kwargs):
    coeffs = np.polyfit(x, d, 2)
    return np.poly1d(coeffs)

def warpingFunctionCubic(x, d, **kwargs):
    coeffs = np.polyfit(x, d, 3)
    return np.poly1d(coeffs)

def warpMassSpectra(spectra, warpingFunctions, emptyNoMatches=False):
    warpedSpectra = []
    for spectrum, wf in zip(spectra, warpingFunctions):
        if wf is None:
            if emptyNoMatches:
                warpedSpectra.append({'Mass': spectrum['Mass'], 'Intensity': np.zeros_like(spectrum['Mass'])})
            continue
        mass = spectrum[0][0:]
        intensity = spectrum[1][0:]
        print("warpingfunctions", warpingFunctions)
        warpedMass = mass + wf(mass)
        warpedSpectra.append({'Mass': warpedMass, 'Intensity': intensity})
    return warpedSpectra
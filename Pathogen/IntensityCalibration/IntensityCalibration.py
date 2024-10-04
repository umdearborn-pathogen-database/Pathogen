import numpy as np
from Pathogen.Dependencies.Global import printMessage

def calibrateIntensity(spectrum, method):
    if(method == "TIC"):
        calibrated_dataframes = [] 
        for df in spectrum:
            scalingFactor = totalIonCurrent(df)
            df['Intensity'] /= scalingFactor
            calibrated_dataframes.append(df)
        return df
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
        printMessage("err", "Issue calibrating intensity. Method is incorrectly defined.")
    
    # Before TIC Normalization
    # Mass   Intensity
    # 100    200
    # 150    300
    # 200    500

    # After TIC Normalization
    # Mass   Normalized Intensity
    # 100    0.2   (200 / 1000)
    # 150    0.3   (300 / 1000)
    # 200    0.5   (500 / 1000)

# def tic_normalization(df):
#     """
#     Perform TIC normalization on the 'Intensity' column of the DataFrame.

#     Parameters:
#     df (pd.DataFrame): Input DataFrame with a column 'Intensity' of type float64.

#     Returns:
#     pd.DataFrame: A new DataFrame with TIC-normalized 'Intensity' values.
#     """
#     if 'Intensity' not in df.columns:
#         raise ValueError("DataFrame must contain an 'Intensity' column.")

#     # Calculate the Total Ion Current (TIC)
#     tic = df['Intensity'].sum()

#     # Normalize the 'Intensity' column
#     # changing this to just change the original Intensity column
#     #df['Normalized_Intensity'] = df['Intensity'] / tic
#     df['Intensity'] = df['Intensity'] / tic
#     return df

# Example usage:
# df = pd.DataFrame({'Mass': [100, 150, 200], 'Intensity': [200.0, 300.0, 500.0]})
# normalized_df = tic_normalization(df)
# print(normalized_df)

# commenting this out for now
def totalIonCurrent(spectrum):
    intensities = spectrum['Intensity'].values
    masses = spectrum['Mass'].values
    left = intensities[:-1].astype(np.float64)
    right = intensities[1:].astype(np.float64)
    massDiff = np.diff(masses).astype(np.float64)
    return np.sum(((left + right) / 2.0) * massDiff)

def medianScalingFactor(spectrum):
    return np.median(spectrum['Intensity'])
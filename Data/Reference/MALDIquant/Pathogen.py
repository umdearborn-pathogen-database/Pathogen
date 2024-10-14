# import os
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.signal import find_peaks
# from sklearn.decomposition import PCA
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import AgglomerativeClustering
# import seaborn as sns

# def import_spectra_from_directory(directory_path):
#     """Imports all mass spectrometry data from CSV files in a specified directory."""
#     all_spectra = []
#     for filename in os.listdir(directory_path):
#         if filename.endswith('.csv'):
#             file_path = os.path.join(directory_path, filename)
#             spectra = pd.read_csv(file_path)
#             all_spectra.append(spectra)
#     return pd.concat(all_spectra, ignore_index=True)

# def import_spectra(file_path):
#     """Imports mass spectrometry data from a CSV file."""
#     return pd.read_csv(file_path)

# def trim_spectra(spectra, min_mz, max_mz):
#     """Trims the spectra to a specified m/z range."""
#     return spectra[(spectra['Mass'] >= min_mz) & (spectra['Mass'] <= max_mz)]

# def estimate_baseline(spectrum):
#     """Estimates the baseline of a spectrum (placeholder function)."""
#     # Here you could implement a more sophisticated baseline estimation method
#     return np.polyval(np.polyfit(spectrum['Mass'], spectrum['Intensity'], 2), spectrum['Mass'])

# def remove_baseline(spectrum, baseline):
#     """Removes the baseline from the spectrum."""
#     spectrum['Intensity'] = np.maximum(spectrum['Intensity'] - baseline, 0)
#     return spectrum

# def calibrate_intensity(spectra):
#     """Calibrates the intensity of the spectra using Total Ion Current (TIC)."""
#     for i in range(len(spectra)):
#         tic = spectra['Intensity'].sum()
#         spectra['Intensity'] = spectra['Intensity'] / tic
#     return spectra

# from scipy.interpolate import interp1d

# def align_spectra(spectrum, target_mass_range):
#     """Aligns the spectrum to a common mass range using interpolation."""
#     print(spectrum.shape, spectrum.head(), type(spectrum))
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

# def detect_peaks(spectrum):
#     """Detects peaks in the spectrum."""
#     peaks, _ = find_peaks(spectrum['Intensity'], height=0.01)  # Adjust threshold as needed
#     return peaks

# def create_feature_matrix(peaks, aligned_spectra):
#     """Creates a feature matrix from detected peaks."""
#     feature_matrix = []
    
#     # Iterate over the peaks
#     for peak in peaks:
#         feature_row = []
        
#         # Since aligned_spectra is a single DataFrame, we can directly access its intensity values
#         feature_row.append(aligned_spectra['Intensity'][peak])  # Access intensity for the peak
        
#         feature_matrix.append(feature_row)
    
#     return np.array(feature_matrix)

# def perform_pca(feature_matrix):
#     """Performs PCA on the feature matrix."""
#     scaler = StandardScaler()
#     feature_matrix_scaled = scaler.fit_transform(feature_matrix)
#     pca = PCA(n_components=2)
#     principal_components = pca.fit_transform(feature_matrix_scaled)
#     return principal_components

# def plot_pca(principal_components, labels):
#     """Plots the PCA results."""
#     plt.figure(figsize=(10, 8))
#     sns.scatterplot(x=principal_components[:, 0], y=principal_components[:, 1], hue=labels, palette="deep")
#     plt.title("PCA of Mass Spectrometry Data")
#     plt.xlabel("Principal Component 1")
#     plt.ylabel("Principal Component 2")
#     plt.legend()
#     plt.show()

# def hierarchical_clustering(feature_matrix):
#     """Performs hierarchical clustering on the feature matrix."""
#     clustering = AgglomerativeClustering(distance_threshold=0, n_clusters=None)
#     clustering.fit(feature_matrix)
#     return clustering

# def save_to_csv(data, filename):
#     """Saves a DataFrame or NumPy array to a CSV file."""
#     if isinstance(data, pd.DataFrame):
#         data.to_csv(filename, index=False)
#     elif isinstance(data, np.ndarray):
#         np.savetxt(filename, data, delimiter=",")
#     else:
#         raise ValueError("Data must be a pandas DataFrame or a NumPy array.")

# def main():
#     # Load and process the data
#     spectra_info = import_spectra("info-ecoli-MAI.csv")
#     spectra_directory = "MAI-redo-ecoli"  # Directory containing CSV files
#     spectra = import_spectra_from_directory(spectra_directory)

#     # Data preprocessing
#     trimmed_spectra = trim_spectra(spectra, 200, 1995)  # Adjust mass range as needed
    
#     # Debugging output to check the structure of trimmed_spectra
#     print(f"Type of trimmed_spectra: {type(trimmed_spectra)}")
#     print(f"Length of trimmed_spectra: {len(trimmed_spectra)}")
#     print(f"Sample of trimmed_spectra:\n{trimmed_spectra.head()}")

#     baseline = estimate_baseline(trimmed_spectra)
#     trimmed_spectra = remove_baseline(trimmed_spectra, baseline)

#     # Align spectra
#     target_mass_range = (200, 1995)  # Specify your target mass range
#     aligned_spectra = align_spectra(trimmed_spectra, target_mass_range)

#     # Peak detection
#     peaks = detect_peaks(aligned_spectra)

#     # Create feature matrix
#     feature_matrix = create_feature_matrix(peaks, aligned_spectra)

#     # PCA analysis
#     principal_components = perform_pca(feature_matrix)
#     plot_pca(principal_components, spectra_info['Bacteria'])

#     # Hierarchical clustering
#     clustering = hierarchical_clustering(feature_matrix)

#     save_to_csv(feature_matrix, "feature_matrix.csv")
#     save_to_csv(principal_components, "pca_results.csv")

def main():
    print()

if __name__ == "__main__":
    main()

### AllClasses.R
### AllGenerics.R
### Deprecated.R
#DONE# alignSpectra-functions.R
### approxfun-methods.R
### as-methods.R
### as.list-functions.R
### as.matrix-functions.R
### as.matrix-methods.R
### averageMassSpectra-functions.R
### binPeaks-functions.R
### calculateLabelPositions-functions.R
### calibrateIntensity-functions.R
### calibrateIntensity-methods.R
### colMedians-functions.R
### constructor-functions.R
### coordinates-methods.R
### deprecated-functions.R
### detectPeaks-methods.R
### determineWarpingFunctions-functions.R
### doByLabels-functions.R
### estimateBaseline-functions.R
### estimateBaseline-methods.R
### estimateNoise-functions.R
### estimateNoise-methods.R
### filterPeaks-functions.R
### findEmptyMassObjects-functions.R
### findLocalMaxima-methods.R
### grouper-functions.R
### intensity-methods.R
### intensityMatrix-functions.R
### irregular-functions.R
### isEmpty-methods.R
### isFunctionList-functions.R
### isMassObject-functions.R
### isMassObjectList-functions.R
### isRegular-methods.R
### isValidHalfWindowSize-functions.R
### labelPeaks-methods.R
### lapply-functions.R
### length-methods.R
### lines-methods.R
### localMaxima-functions.R
### mapply-functions.R
### mass-methods.R
### match.closest-functions.R
### memoryUsage-functions.R
### merge-functions.R
### metaData-methods.R
### monoisotopic-functions.R
### monoisotopicPeaks-methods.R
### morphologicalFilter-functions.R
### msiSlices-functions.R
### mz-methods.R
### onAttach.R
### plot-methods.R
### plotMsiSlice-functions.R
### plotMsiSlice-methods.R
### points-methods.R
### range-functions.R
### referencePeaks-functions.R
### removeBaseline-methods.R
### removeEmptyMassObjects-functions.R
### reorder-functions.R
### replaceNegativeIntensityValues-functions.R
### show-functions.R
### show-methods.R
### smoothIntensity-methods.R
### smoothingFilters-functions.R
### snr-methods.R
### subset-methods.R
### totalIonCurrent-methods.R
### transformIntensity-methods.R
### trim-methods.R
### unlist-functions.R
### valid-methods.R
### warp-functions.R
### warpingFunction-functions.R













# WORKSPACE

# #!/usr/bin/env Rscript
# install.packages(c("sda", "crossval", "devtools", "pca3d","FactoMineR", "factoextra", "dendextend", "MALDIquant", "MALDIquantForeign"))
# library("devtools")
# library("MALDIquant")
# library("MALDIquantForeign")
# library("sda")
# library("pca3d")
# library(dendextend)
# library("sda")
# library(factoextra)
# library(FactoMineR)

# Loading in the header data
# spectra.info  - data frame
# read.csv      - base R function, imports into an R data frame
# "info-ecoli-MAI.csv"  - metadata file
#                       - contains information:
#                           - patientID
#                           - Bacteria
# header=TRUE   - When TRUE, R treats the first row of the file as the
#                   names of the columns in the resulting data frame
# value returns a dataframe
# spectra.info <- read.csv("info-ecoli-MAI.csv", header=TRUE)

# Commented out in the R script
# #View(spectra.info)

# Loading in the mass spec data
# spectra       - list of mass spectrometry objects
# importCsv     - MALDIquantForeign method, removes empty spectra
# value returns a list of mass spectrometry objects
# spectra <- importCsv("MAI-redo-ecoli")

# Checks to see if any of the spectra in the spectra list are empty, any() will return TRUE
# any()     - takes a logical vector and checks if ANY of the values are TRUE
# sapply()  - applies a function to each element of a list of vector and simplifies 
#               the result into a vector or matrix
# isEmpty() - from MALDIquant, checks whether a spectrum is empty, meaning that the
#               spectrum does not contain any mass-to-charge ration (m/z) values or 
#               intensity values, returns TRUE if empty
# value returns a boolean
# any(sapply(spectra, isEmpty))

# Generates a vector of integers, where each integer represents the number of
#               data points (m/z values) for each spectrum in the list
# table()   - takes the vector output from sapply(spectra, length) and creates
#               a frequency table showing how many spectra have the same number
#               of data points (i.e., the same length)
# sapply()  - applies a function to each element of a list of vector and simplifies 
#               the result into a vector or matrix
# spectra   - mass spectrometry objects
# length    - is the function applied to each spectrum in the spectra list.
#               It returns the number of m/z values (or data points) in each spectrum
# table(sapply(spectra, length))

# all(sapply(spectra, isRegular))
# spectra <- trim(spectra, range=c(200, 1995))
# baseline <- estimateBaseline(spectra[[1]], method="SNIP",iterations=150)
# plot(spectra[[1]])
# lines(baseline, col="red", lwd=2)
# spectra <- removeBaseline(spectra, method="SNIP",iterations=150)
# plot(spectra[[1]])
# spectra <- calibrateIntensity(spectra, method="TIC")

# spectra <- alignSpectra(spectra)
# avgSpectra <-averageMassSpectra(spectra, labels=spectra.info$patientID)
# avgSpectra.info <-spectra.info[!duplicated(spectra.info$patientID), ]
# noise <- estimateNoise(avgSpectra[[1]])
# plot(avgSpectra[[1]], xlim=c(200, 2000), ylim=c(0, 0.10))
# lines(noise, col="red") # SNR == 1
# lines(noise[, 1], 2*noise[, 2], col="blue")
# peaks <- detectPeaks(avgSpectra, SNR=2, halfWindowSize=20)
# peaks <- binPeaks(peaks)
# peaks <- filterPeaks(peaks, minFrequency=c(0.2),labels=avgSpectra.info$Bacteria, mergeWhitelists=TRUE)
# featureMatrix <- intensityMatrix(peaks, avgSpectra)
# #exclude varibles
# #featureMatrix <- featureMatrix[,-c(726:730)]

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
# pca2d(pca, group=gr, legend="topleft")
# pca3d(pca, group=gr, show.ellipses=TRUE, ellipse.ci=0.75, show.plane=FALSE, legend="topleft")

# res.pca <- PCA(featureMatrix, scale.unit=TRUE, ncp=2,graph = FALSE)
# res.hcpc <- HCPC(res.pca, graph = FALSE)
# fviz_dend(res.hcpc,cex = 0.55, palette = "jco", rect = TRUE, rect_fill = FALSE, rect_border = "jco", labels_track_height = 300.0,H =0.5)

# Commented out in the R script
# #savehistory(file = ".chuping.txt")



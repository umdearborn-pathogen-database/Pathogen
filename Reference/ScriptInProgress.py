# Notes:
#   pyOpenMS

# Install the necessary packages
# R > install.packages(c("sda", "crossval", "devtools", "pca3d","FactoMineR", "factoextra", "dendextend", "MALDIquant", "MALDIquantForeign"))
# Python > WIP

# Load the required libraries
#   devtools            - data manipulation
#   sda                 - data manipulation
#   MALDIquant          - mass spectrometry analysis
#   MALDIquantForeign   - mass spectrometry analysis
#   pca3d               - principal component analysis
#   FactoMineR          - principal component analysis
#   factoextra          - principal component analysis
#   dendextend          - clustering
# R > library("devtools")
# Python > WIP
# R > library("MALDIquant")
# Python > WIP
# R > library("MALDIquantForeign")
# Python > WIP
# R > library("sda")
# Python > WIP
# R > library("pca3d")
# Python > WIP
# R > library(dendextend)
# Python > WIP
# R > library("sda")
# Python > WIP
# R > library(factoextra)
# Python > WIP
# R > library(FactoMineR)
# Python > WIP

# Read the metadata file
#   header=TRUE specifies that the first row of the CSV file
#       contains column names
# R > spectra.info <- read.csv("info-ecoli-MAI.csv", header=TRUE)
# Python > Complete

# R > #View(spectra.info)
# Python > Commented out in R

# Import the spectra data
# R > spectra <- importCsv("MAI-redo-ecoli")
# Python > spectra = pd.read_csv('Data/Import/MAI-redo-ecoli/')
#   * Error of directory, not file is thrown -- needs a method to read in all of the files within the directory

# Check for any empty spectra
# R > any(sapply(spectra, isEmpty))
# Python > any(map(isEmpty, spectra))
#   - isEmpty*

# Display the distribution of spectra lengths
# R > table(sapply(spectra, length))
#   - table*
#   - length*
# Python > ...

# Check if all spectra are regularly spaced
# R > all(sapply(spectra, isRegular))
#   - isRegular*
# Python > ...

# Trim the spectra to a specified mass range
# R > spectra <- trim(spectra, range=c(200, 1995))
# Python > ...

# Estimate the baseline using the SNIP method
# R > baseline <- estimateBaseline(spectra[[1]], method="SNIP",iterations=150)
# Python > ...

# Plot the first spectrum with the baseline overlaid in red
# R > plot(spectra[[1]])
# Python > ...
# R > lines(baseline, col="red", lwd=2)
# Python > ...

# Remove the baseline fromt he spetra using the SNIP method
# R > spectra <- removeBaseline(spectra, method="SNIP",iterations=150)
# Python > ...

# Plot the first spectrum after baseline removal
# R > plot(spectra[[1]])
# Python > ...

# Calibrate the intensity of the spectra using the TIC method
# R > spectra <- calibrateIntensity(spectra, method="TIC")
# Python > ...

# Align the spectra
# R > spectra <- alignSpectra(spectra)
# Python > ...

# Calculate the average spectra for each patient
# R > avgSpectra <-averageMassSpectra(spectra, labels=spectra.info$patientID)
# Python > ...

# Filter out duplicated patient IDs
# R > avgSpectra.info <-spectra.info[!duplicated(spectra.info$patientID), ]
# Python > ...

# Estimate the noise in the first averaged spectrum
# R > noise <- estimateNoise(avgSpectra[[1]])
# Python > ...

# Plot the averaged spectrum with noise levels
# R > plot(avgSpectra[[1]], xlim=c(200, 2000), ylim=c(0, 0.10))
# Python > ...
# R > lines(noise, col="red") # SNR == 1
# Python > ...
# R > lines(noise[, 1], 2*noise[, 2], col="blue")
# Python > ...

# Detect peaks in the averaged spectra with a specified signal-to-noise ration (SNR)
# R > peaks <- detectPeaks(avgSpectra, SNR=2, halfWindowSize=20)
# Python > ...

# Bin the detected peaks
# R > peaks <- binPeaks(peaks)
# Python > ...

# Filter the peaks based on frequency and merge whitelists
# R > peaks <- filterPeaks(peaks, minFrequency=c(0.2),labels=avgSpectra.info$Bacteria, mergeWhitelists=TRUE)
# Python > ...

# Create a feature matrix based on peak intensities
# R > featureMatrix <- intensityMatrix(peaks, avgSpectra)
# Python > ...

#exclude varibles

# R > #featureMatrix <- featureMatrix[,-c(726:730)]
# Python > Commented out in R

# Set row names of the feature matrix to patient IDs
# R > rownames(featureMatrix) <- avgSpectra.info$patientID
# Python > ...

# Define training data (Xtrain) and labels (Ytrain)
# R > Xtrain <- featureMatrix
# Python > ...
# R > Ytrain <- avgSpectra.info$Bacteria
# Python > ...

# Perform sda ranking
# R > ddar <- sda.ranking(Xtrain=featureMatrix, L=Ytrain, fdr=FALSE,diagonal=TRUE)
# Python > ...

# Calculate the distance matrix using Euclidean distance
# R > distanceMatrix <- dist(featureMatrix, method="euclidean")
# Python > ...

# Perform hierarchical clustering using the complete linkage method
# R > hClust <- hclust(distanceMatrix, method="complete")
# Python > ...

# Plot the hierarchical clustering dendrogram
# R > plot(hClust, hang=-1)
# Python > ...

# Save the feature matrix to a CSV file
# R > write.csv(featureMatrix, file = "PCA1.csv")
# Python > ...

# Read the CSV file back into R
# R > z <- read.csv(file = 'PCA1.csv', header = TRUE)
# Python > ...



# Perform PCA on the feature matrix, excluding the first column
# R > pca <- prcomp(z[,-1], scale.=TRUE)
# Python > ...

# Group labels based on bacteria types
# R > gr <- factor(z[,1], labels=avgSpectra.info$Bacteria)
# Python > ...

# Summarize the group labels
# R > summary(gr)
# Python > ...

# Plot 2D PCA
# R > pca2d(pca, group=gr, legend="topleft")
# Python > ...

# Plot 3D PCA with ellipses
# R > pca3d(pca, group=gr, show.ellipses=TRUE, ellipse.ci=0.75, show.plane=FALSE, legend="topleft")
# Python > ...

# Perform PCA and hierarchical clustering on principal components (HCPC)
# R > res.pca <- PCA(featureMatrix, scale.unit=TRUE, ncp=2,graph = FALSE)
# Python > ...
# R > res.hcpc <- HCPC(res.pca, graph = FALSE)
# Python > ...

# Visualize the dendrogram from NCPC with custom settings
# R > fviz_dend(res.hcpc,cex = 0.55, palette = "jco", rect = TRUE, rect_fill = FALSE, rect_border = "jco", labels_track_height = 300.0,H =0.5)
# Python > ...

# R > #savehistory(file = ".chuping.txt")
# Python > Commented out in R
#!/usr/bin/env Rscript

# Comments generated from ChatGPT
#   Anything with a comment by itself is originally commented out code

# Install the necessary packages
install.packages(c("sda", "crossval", "devtools", "pca3d","FactoMineR", "factoextra", "dendextend", "MALDIquant", "MALDIquantForeign"))

# Load the required libraries
#   devtools            - data manipulation
#   sda                 - data manipulation
#   MALDIquant          - mass spectrometry analysis
#   MALDIquantForeign   - mass spectrometry analysis
#   pca3d               - principal component analysis
#   FactoMineR          - principal component analysis
#   factoextra          - principal component analysis
#   dendextend          - clustering
library("devtools")
library("MALDIquant")
library("MALDIquantForeign")
library("sda")
library("pca3d")
library(dendextend)
library("sda")
library(factoextra)
library(FactoMineR)

# Read the metadata file
#   header=TRUE specifies that the first row of the CSV file
#       contains column names
spectra.info <- read.csv("info-ecoli-MAI.csv", header=TRUE)

#View(spectra.info)

# Import the spectra data
spectra <- importCsv("MAI-redo-ecoli")

# Check for any empty spectra
any(sapply(spectra, isEmpty))

# Display the distribution of spectra lengths
table(sapply(spectra, length))

# Check if all spectra are regularly spaced
all(sapply(spectra, isRegular))

# Trim the spectra to a specified mass range
spectra <- trim(spectra, range=c(200, 1995))

# Estimate the baseline using the SNIP method
baseline <- estimateBaseline(spectra[[1]], method="SNIP",iterations=150)

# Plot the first spectrum with the baseline overlaid in red
plot(spectra[[1]])
lines(baseline, col="red", lwd=2)

# Remove the baseline fromt he spetra using the SNIP method
spectra <- removeBaseline(spectra, method="SNIP",iterations=150)

# Plot the first spectrum after baseline removal
plot(spectra[[1]])

# Calibrate the intensity of the spectra using the TIC method
spectra <- calibrateIntensity(spectra, method="TIC")

# Align the spectra
spectra <- alignSpectra(spectra)

# Calculate the average spectra for each patient
avgSpectra <-averageMassSpectra(spectra, labels=spectra.info$patientID)

# Filter out duplicated patient IDs
avgSpectra.info <-spectra.info[!duplicated(spectra.info$patientID), ]

# Estimate the noise in the first averaged spectrum
noise <- estimateNoise(avgSpectra[[1]])

# Plot the averaged spectrum with noise levels
plot(avgSpectra[[1]], xlim=c(200, 2000), ylim=c(0, 0.10))
lines(noise, col="red") # SNR == 1
lines(noise[, 1], 2*noise[, 2], col="blue")

# Detect peaks in the averaged spectra with a specified signal-to-noise ration (SNR)
peaks <- detectPeaks(avgSpectra, SNR=2, halfWindowSize=20)

# Bin the detected peaks
peaks <- binPeaks(peaks)

# Filter the peaks based on frequency and merge whitelists
peaks <- filterPeaks(peaks, minFrequency=c(0.2),labels=avgSpectra.info$Bacteria, mergeWhitelists=TRUE)

# Create a feature matrix based on peak intensities
featureMatrix <- intensityMatrix(peaks, avgSpectra)

#exclude varibles

#featureMatrix <- featureMatrix[,-c(726:730)]

# Set row names of the feature matrix to patient IDs
rownames(featureMatrix) <- avgSpectra.info$patientID

# Define training data (Xtrain) and labels (Ytrain)
Xtrain <- featureMatrix
Ytrain <- avgSpectra.info$Bacteria

# Perform sda ranking
ddar <- sda.ranking(Xtrain=featureMatrix, L=Ytrain, fdr=FALSE,diagonal=TRUE)

# Calculate the distance matrix using Euclidean distance
distanceMatrix <- dist(featureMatrix, method="euclidean")

# Perform hierarchical clustering using the complete linkage method
hClust <- hclust(distanceMatrix, method="complete")

# Plot the hierarchical clustering dendrogram
plot(hClust, hang=-1)

# Save the feature matrix to a CSV file
write.csv(featureMatrix, file = "PCA1.csv")

# Read the CSV file back into R
z <- read.csv(file = 'PCA1.csv', header = TRUE)



# Perform PCA on the feature matrix, excluding the first column
pca <- prcomp(z[,-1], scale.=TRUE)

# Group labels based on bacteria types
gr <- factor(z[,1], labels=avgSpectra.info$Bacteria)

# Summarize the group labels
summary(gr)

# Plot 2D PCA
pca2d(pca, group=gr, legend="topleft")

# Plot 3D PCA with ellipses
pca3d(pca, group=gr, show.ellipses=TRUE, ellipse.ci=0.75, show.plane=FALSE, legend="topleft")

# Perform PCA and hierarchical clustering on principal components (HCPC)
res.pca <- PCA(featureMatrix, scale.unit=TRUE, ncp=2,graph = FALSE)
res.hcpc <- HCPC(res.pca, graph = FALSE)

# Visualize the dendrogram from NCPC with custom settings
fviz_dend(res.hcpc,cex = 0.55, palette = "jco", rect = TRUE, rect_fill = FALSE, rect_border = "jco", labels_track_height = 300.0,H =0.5)

#savehistory(file = ".chuping.txt")
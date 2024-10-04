install.packages(c("MALDIquant", "MALDIquantForeign","sda","crossval", "devtools", "pca3d"))
library("devtools")
library("MALDIquant")
library("MALDIquantForeign")
library("sda")
library(pca3d)


spectra.info <- read.csv("info-TCE-Final-unknown.csv", header=TRUE)
View(spectra.info)
spectra <- importCsv("CE-Final-unknown")
any(sapply(spectra, isEmpty))
table(sapply(spectra, length))
all(sapply(spectra, isRegular))
spectra <- trim(spectra, range=c(200, 1995))
baseline <- estimateBaseline(spectra[[1]], method="SNIP",iterations=150)
plot(spectra[[1]])
lines(baseline, col="red", lwd=2)
spectra <- removeBaseline(spectra, method="SNIP",
iterations=150)
plot(spectra[[1]])
spectra <- calibrateIntensity(spectra, method="TIC")
spectra <- alignSpectra(spectra)
avgSpectra <-averageMassSpectra(spectra, labels=spectra.info$patientID)
avgSpectra.info <-spectra.info[!duplicated(spectra.info$patientID), ]
noise <- estimateNoise(avgSpectra[[1]])
plot(avgSpectra[[1]], xlim=c(200, 2000), ylim=c(0, 0.10))
lines(noise, col="red") # SNR == 1
lines(noise[, 1], 2*noise[, 2], col="blue")
peaks <- detectPeaks(avgSpectra, SNR=2, halfWindowSize=20)
peaks <- binPeaks(peaks)
peaks <- filterPeaks(peaks, minFrequency=c(0.5, 0.5),labels=avgSpectra.info$Bacteria, mergeWhitelists=TRUE)
featureMatrix <- intensityMatrix(peaks, avgSpectra)
rownames(featureMatrix) <- avgSpectra.info$patientID
library("sda")
Xtrain <- featureMatrix
Ytrain <- avgSpectra.info$Bacteria
ddar <- sda.ranking(Xtrain=featureMatrix, L=Ytrain, fdr=FALSE,
diagonal=TRUE)
distanceMatrix <- dist(featureMatrix, method="euclidean")
hClust <- hclust(distanceMatrix, method="complete")
plot(hClust, hang=-1)
#write.csv(featureMatrix, file = "unknown.csv")



#z <- read.csv(file = 'unknown.csv', header = TRUE)
pca <- prcomp(featureMatrix [,-1], scale.=TRUE)
gr <- factor(featureMatrix [,1], labels=avgSpectra.info$Bacteria)
summary(gr)
pca2d(pca, group=gr, legend="topleft")
pca3d(pca, group=gr, show.ellipses=TRUE, ellipse.ci=0.75, show.plane=FALSE, legend="topleft")
snapshotPCA3d(file="ellipses.tiff")
savehistory(file = ".chuping.txt")
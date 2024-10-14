# R/calibrateIntensity-functions.R and calibrateIntensity-methods.R

# R/calibrateIntensity-functions.R

# ## .scalingFactor
# ## calculate scaling factor for TIC/median ranged calibration
# ##
# ## params:
# ##  object: AbstractMassObject
# ##  method: character
# ##  range: double
# ##
# ## returns:
# ##  double
# ##
# .scalingFactor <- function(object, method=c("TIC", "median"), range) {

#   method <- match.arg(method)

#   if (!missing(range)) {
#     object <- trim(object, range=range)
#   }

#   switch(method,
#     "TIC" = {
#       totalIonCurrent(object)
#     },
#     "median" = {
#       median(object@intensity)
#     }
#   )
# }

# ## .calibrateIntensitySimple
# ## calibrate intensity values by offset and scaling factor
# ##
# ## params:
# ##  y: double, intensity values
# ##  offset: double
# ##  scaling: double
# ##
# ## returns:
# ##  double, calibrated intensity values
# ##
# .calibrateIntensitySimple <- function(y, offset=0L, scaling=1L) {
#   if (scaling == 0L) {
#     warning("Scaling factor is zero. No calibration applied.")
#     y
#   } else {
#     (y - offset) / scaling
#   }
# }

# ## .calibrateProbabilisticQuotientNormalization
# ## calibrate intensity values by Probabilistic Quotient Normalization
# ##
# ## F. Dieterle, A. Ross, G. Schlotterbeck, and Hans Senn.
# ## "Probabilistic quotient normalization as robust method to account for
# ## dilution of complex biological mixtures. Application in 1H NMR
# ## metabonomics."
# ## Analytical Chemistry 78, no. 13 (2006): 4281-4290.
# ##
# ## 1. Perform an integral normalization (typically a constant
# ##    integral of 100 is used).
# ## 2. Choose/calculate the reference spectrum (the best approach
# ##    is the calculation of the median spectrum of control samples).
# ## 3. Calculate the quotients of all variables of interest of the test
# ##    spectrum with those of the reference spectrum.
# ## 4. Calculate the median of these quotients.
# ## 5. Divide all variables of the test spectrum by this median.
# ##
# ## params:
# ##  l: list of MassSpectrum objects
# ##  range: double
# ##
# ## returns:
# ##  list of calibrated MassSpectrum objects
# ##
# .calibrateProbabilisticQuotientNormalization <- function(l, range) {
#   ## 1. integral normalization (==TIC)
#   l <- calibrateIntensity(l, method="TIC", range=range)
#   ## 2. median reference spectrum
#   if (missing(range)) {
#     reference <- .averageMassSpectra(l, fun=.colMedians, mergeMetaData=FALSE)
#   } else {
#     reference <- .averageMassSpectra(trim(l, range=range), fun=.colMedians,
#                                      mergeMetaData=FALSE)
#   }

#   lapply(l, function(x) {
#     ## 3. quotient calculation
#     q <- approxfun(x)(reference@mass) / reference@intensity
#     ## 4. median
#     m <- median(q, na.rm=TRUE)
#     ## 5. divide by median
#     .transformIntensity(x, fun=.calibrateIntensitySimple, offset=0L, scaling=m)
#   })
# }





# R/calibrateIntensity-methods.R

# ## MassSpectrum
# setMethod(f="calibrateIntensity",
#           signature=signature(object="MassSpectrum"),
#           definition=function(object,
#                               method=c("TIC", "PQN", "median"),
#                               range, ...) {

#   method <- match.arg(method)

#   switch(method,
#     "TIC" = ,
#     "median" = {
#       .transformIntensity(object, fun=.calibrateIntensitySimple,
#                           offset=0L,
#                           scaling=.scalingFactor(object, method=method,
#                                                  range=range))
#     },
#     "PQN" = {
#       stop(dQuote("PQN"),
#            " is not supported for a single MassSpectrum object.")
#     })
# })

# ## list
# setMethod(f="calibrateIntensity",
#           signature=signature(object="list"),
#           definition=function(object,
#                               method=c("TIC", "PQN", "median"), range, ...) {

#   ## test arguments
#   .stopIfNotIsMassSpectrumList(object)

#   method <- match.arg(method)

#   switch(method,
#     "TIC" = ,
#     "median" = {
#       .lapply(object, calibrateIntensity, method=method, range=range, ...)
#     },
#     "PQN" = {
#       .calibrateProbabilisticQuotientNormalization(object, range=range)
#     }
#   )
# })
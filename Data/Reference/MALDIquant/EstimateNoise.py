# R/estimateNoise-functions.R and R/estimateNoise-methods.R

# R/estimateNoise-functions.R

# ## .estimateNoise
# ##  estimating the noise of a spectrum
# ##
# ## params:
# ##  x: vector of x values (mass)
# ##  y: vector of y values (intensity)
# ##  method: method to use
# ##  ...: further arguments passed to "method"
# ##
# ## returns:
# ##  numeric, estimated noise (y)
# ##
# .estimateNoise <- function(x, y, method=c("MAD", "SuperSmoother"), ...) {

#   method <- match.arg(method)

#   switch(method,
#          "MAD" = {
#            .estimateNoiseMad(x, y)
#          },
#          "SuperSmoother" = {
#            .estimateNoiseSuperSmoother(x, y, ...)
#          }
#   )
# }

# ## estimateNoiseMad
# ##  estimate noise by calculating mad over intensity values
# ##
# ## params:
# ##  x: vector of x values
# ##  y: vector of y values
# ##
# ## returns:
# ##  numeric, estimated noise (y)
# ##
# .estimateNoiseMad <- function(x, y) {
#   rep.int(stats::mad(y), length(x))
# }

# ## estimateNoiseSuperSmoother
# ##  estimate noise by using Friedman's super smoother
# ##
# ## params:
# ##  x: vector of x values
# ##  y: vector of y values
# ##  ...: further arguments to passed to supsmu
# ##
# ## returns:
# ##  numeric, estimated noise (y)
# ##
# .estimateNoiseSuperSmoother <- function(x, y, ...) {
#   stats::supsmu(x=x, y=y, ...)$y
# }





# R/estimateNoise-methods.R

# ## MassSpectrum
# setMethod(f="estimateNoise",
#           signature=signature(object="MassSpectrum"),
#           definition=function(object, method=c("MAD", "SuperSmoother"),
#                               ...) {
#   if (.isEmptyWarning(object)) {
#     return(0L)
#   }

#   cbind(mass=object@mass,
#         intensity=.estimateNoise(x=object@mass, y=object@intensity,
#                                  method=method, ...))
# })
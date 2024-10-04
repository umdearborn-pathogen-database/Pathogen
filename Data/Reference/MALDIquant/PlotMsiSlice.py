# R/plotMsiSlice-functions.R and R/plotMsiSlice-methods.R

# R/plotMsiSlice-functions.R

# .plotMsiSlice <- function(x, center=attr(x, "center"),
#                           tolerance=attr(x, "tolerance"),
#                           colRampList=list(colorRamp(c("black", "blue", "green",
#                                                        "yellow", "red"))),
#                           xlab="", ylab="", interpolate=FALSE, scale=TRUE,
#                           legend=scale, alignLabels=FALSE, label.cex=0.75,
#                           label.col=NULL, ...) {
#   stopifnot(is.array(x))

#   d <- dim(x)
#   tolerance <- rep_len(tolerance, length(center))

#   xlim <- c(0L, d[1L] + (2L * d[3L] * legend))
#   ylim <- c(0L, d[2L])

#   ## prepare plot area
#   plot(NA, type="n", xlim=xlim, ylim=ylim,
#        axes=FALSE, xlab=xlab, ylab=ylab, asp=1L, ...)

#   if (d[3L] > 1L) {
#     col <- x

#     for (i in seq_len(d[3L])) {
#       col[,, i] <- .colorMatrix(.array2matrix(x, z=i), colRamp=colRampList[[i]],
#                                 scale=scale)
#     }

#     x <- .combineColorMatrices(x, col)
#   } else {
#     x <- .colorMatrix(.array2matrix(x), colRamp=colRampList[[1L]], scale=scale)
#   }

#   ## plot image
#   .rasterSlice(x, interpolate=interpolate)

#   if (legend) {

#     if (!is.null(center)) {
#       labels <- .mapply(function(cnt, tol)bquote(.(cnt) %+-% .(tol)),
#                         cnt=center, tol=tolerance)
#       strh <- max(strheight(labels, cex=label.cex)) * 1.2
#     } else {
#       labels <- character(d[3L])
#       strh <- 0L
#     }

#     xleft <- xlim[2L] - seq(from=d[3L] * 2L - 1L, to=1L, by=-2L)
#     xright <- xleft + 1L
#     ybottom <- rep.int(d[3L] * strh, d[3L])
#     ytext <- (d[3L] - 1L):0L * strh

#     xtext <- if (alignLabels) {
#       rep.int(xlim[2L], 3L)
#     } else {
#       xright
#     }

#     if (is.null(label.col) && d[3L] == 1L) {
#       label.col <- "black"
#     } else if (is.null(label.col) && d[3L] > 1L) {
#       label.col <- lapply(colRampList, function(x).rgb(x(1L)))
#     }

#     for (i in seq_len(d[3L])) {
#       .msiLegend(xleft=xleft[i], xright=xright[i],
#                  ybottom=ybottom[1L], ytop=ylim[2L],
#                  colRamp=colRampList[[i]], interpolate=interpolate)
#       text(x=xtext[i], y=ytext[i], labels=as.expression(labels[i]),
#            col=label.col[[i]], cex=label.cex, adj=c(1L, 0L))
#     }
#   }
# }

# .rasterSlice <- function(x, interpolate=FALSE) {
#   rasterImage(as.raster(t(x)),
#               xleft=0L, xright=nrow(x), ybottom=0L, ytop=ncol(x),
#               interpolate=interpolate)
# }

# .array2matrix <- function(a, z=1L) {
# ## subset function that preserves a matrix even if x or y 1
# ## ([,,drop=TRUE]) creates a vector
#   d <- dim(a)
#   matrix(a[,, z, drop=TRUE], nrow=d[1L], ncol=d[2L])
# }

# .msiLegend <- function(xleft, xright, ybottom, ytop,
#                        colRamp=colorRamp(c("black", "blue", "green", "yellow",
#                                            "red")), interpolate=FALSE) {
#   gradient <- matrix(.rgb(colRamp(seq.int(1L, 0L, length.out=100L))),
#                      ncol=1L)
#   rect(xleft=xleft, xright=xright, ybottom=ybottom, ytop=ytop,
#        col="black")
#   rasterImage(as.raster(gradient),
#               xleft=xleft, xright=xright, ybottom=ybottom, ytop=ytop,
#               interpolate=interpolate)
# }

# .colorMatrix <- function(x, colRamp, scale=TRUE) {
#   if (scale) {
#     x <- x / max(x, na.rm=TRUE)
#   }

#   notNA <- which(!is.na(x))
#   x[notNA] <- .rgb(colRamp(x[notNA]))
#   x
# }

# .combineColorMatrices <- function(x, col) {
#   i <- apply(x, 2L, max.col, ties.method="first")
#   j <- cbind(x=rep.int(seq_len(nrow(x)), ncol(x)),
#              y=rep(seq_len(ncol(x)), each=nrow(x)),
#              z=as.vector(i))
#   y <- .array2matrix(col)
#   y[] <- col[j]
#   y
# }

# .rgb <- function(x) {
#   rgb(x, maxColorValue=255L)
# }





# R/plotMsiSlice-methods.R

# setMethod(f="plotMsiSlice",
#           signature=signature(x="list"),
#           definition=function(x, center, tolerance,
#                               colRamp=colorRamp(c("black", "blue", "green",
#                                                    "yellow", "red")),
#                               interpolate=FALSE, legend=TRUE, alignLabels=FALSE,
#                               combine=FALSE, ...) {
#   .stopIfNotIsMassObjectList(x)
#   slides <- msiSlices(x, center=center, tolerance=tolerance)
#   plotMsiSlice(slides, colRamp=colRamp, interpolate=interpolate, legend=legend,
#                alignLabels=alignLabels, combine=combine, ...)
# })

# setMethod(f="plotMsiSlice",
#           signature=signature(x="array"),
#           definition=function(x, colRamp=colorRamp(c("black", "blue", "green",
#                                                      "yellow", "red")),
#                               interpolate=FALSE, legend=TRUE, alignLabels=FALSE,
#                               combine=FALSE, plotInteractive=FALSE, ...) {
#   n <- dim(x)[3L]

#   if (!is.list(colRamp)) {
#     colRamp <- rep_len(list(colRamp), n)
#   }

#   if (n != length(colRamp)) {
#     stop(sQuote("dim(x)[3L]"), " (number of centers) has to be the same as ",
#          "the length of the list ", sQuote("colRamp"), "!\n",
#          "See ", sQuote("?plotMsiSlice"), " for details.")
#   }

#   if (combine) {
#    .plotMsiSlice(x, colRampList=colRamp, interpolate=interpolate,
#                   legend=legend, alignLabels=alignLabels, ...)

#   } else {
#     isNonInteractivePlot <- dev.cur() != 1L && !dev.interactive()
#     if (n > 1L && !isNonInteractivePlot && !plotInteractive) {
#       warning(sQuote("plotMsiSlice"), " was called for multiple slices on an ",
#               "interactive device. Only the first slice is plotted. Use ",
#               sQuote("pdf"), " or a similar device to plot all slices at once.",
#               " Alternatively use ", dQuote("combine=TRUE"), " to plot ",
#               "multiple centers in one plot.\n",
#               "See ", sQuote("?plotMsiSlice"), " for details.")
#       n <- 1L
#     }

#     tolerance <- rep_len(attr(x, "tolerance"), n)

#     for (i in seq_len(n)) {
#       .plotMsiSlice(x[,, i, drop=FALSE],
#                     center=attr(x, "center")[i],
#                     tolerance=tolerance[i],
#                     colRampList=colRamp[i], interpolate=interpolate,
#                     legend=legend, ...)
#     }
#   }
# })

# setMethod(f="plotMsiSlice",
#           signature=signature(x="matrix"),
#           definition=function(x, colRamp=colorRamp(c("black", "blue", "green",
#                                                      "yellow", "red")),
#                                 interpolate=FALSE, scale=TRUE, legend=scale,
#                                 ...) {
#   if (!is.list(colRamp)) {
#     colRamp <- list(colRamp)
#   }

#   dim(x) <- c(dim(x), 1L)

#   .plotMsiSlice(x, colRampList=colRamp, interpolate=interpolate, scale=scale,
#                 legend=legend, ...)
# })
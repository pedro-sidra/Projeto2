class SLCalculator:
    """
    Structured Light Calculator

    Uses a line projected on a surface to compute heights
    """
    def __init__(self, refMask,
                ppcm,
                ):

        # Init reference line params:
            # x limits (lower, upper)
            # eigenvectors (perp, parallel)
            # line function f(x) = a*x + b
        self.xlims, self.eig, self.f = sef._init_reference(refMask)

        # Save pixels per cm
        self.ppcm = ppcm

    def _init_reference(self, mask):
        """
        Initiates the Structured Light reference from a binary mask

        input: binary mask of the laser's reference line

        outputs: mask's min and max X value,
                 PCA eigenvectors,
                 line equation
        """

        y, x = np.nonzero(mask)

        points = np.vstack((x, y)).swapaxes(0, 1)

        (mean,), eig = cv2.PCACompute(points.astype('float32'),
                                      mean=None)

        xlims = (np.min(x),np.max(x))
        eig = eig
        f = self._computeLineEquation(eig, mean)

        return xlims, eig, f


    def _computeLineEquation(self, eig, mean):
        v1, v2 = eig

        dx, dy = v1
        a = dy/dx
        b = mean[1] - a*mean[0]
        def f(x): return a*x+b

        return f


    def linePoints(self, samples=100, asInt=True):
        x1, x2 = self.xlims
        px = np.linspace(x1, x2, samples)
        py = self.f(px)

        if asInt:
            points = np.round(np.array((px, py)))
            return points.T.astype(np.int32)
        else:
            return points.T

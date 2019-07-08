import cv2
import numpy as np
import pdb

TEST_H = 332
import matplotlib.pyplot as plt


def lineFromVec(vec, x, y):
    a, b = vec
    c = -a * x - b*y
    def f(x): return (-a*x-c)/b

    return f, (a, b, c)


class SLCalculator:
    """
    Structured Light Calculator

    Uses a line projected on a surface to compute heights
    """

    def __init__(self, refMask,
                 ppcm,
                 tanLaserAngle,
                 axisCenter=(0, 0),
                 CM=None
                 ):

        # Init reference line params:
            # x limits (lower, upper)
            # eigenvectors (perp, parallel)
            # line function f(x) = a*x + b

        self.CM = np.linalg.inv(CM)
        self.axisCenter = axisCenter

        self.xlims, self.eig, (self.f, self.lineParams) = self._init_reference(
            refMask)

        # Save pixels per cm
        self.ppcm = ppcm


        self.tanAlfa = tanLaserAngle

        self.heightFactor = self.tanAlfa/ppcm

    def projectionVector(self, x, y):
        v1, v2 = self.eig
        v1 = v1/np.linalg.norm(v1)
        v2 = v2/np.linalg.norm(v2)
        b = self.f(0)
        mean = self.mean

        dist = self.dist_to_ref(x, y, signed=True)

        pReta = np.array([x, y]) - dist*v2

        return pReta, np.array([x, y])

    def dist_to_ref(self, x, y, signed=False):
        a, b, c = self.lineParams
        if signed:
            return (a*x + b*y + c)/np.sqrt(a**2+b**2)
        else:
            return np.abs(a*x + b*y + c)/np.sqrt(a**2+b**2)

    def _init_reference(self, mask):
        """
        Initiates the Structured Light reference from a binary mask

        input: binary mask of the laser's reference line

        outputs: mask's min and max X value,
                 PCA eigenvectors,
                 line equation
        """

        y, x = np.nonzero(mask)

        pdb.set_trace()
        points = np.vstack((x, y, np.ones_like(y)))

        projs = TEST_H*self.CM@points

        pca_points = projs[:2].swapaxes(0,1).astype('float32')

        (mean,), eig = cv2.PCACompute(pca_points,
                                      mean=None)

        v1, v2 = eig

        self.mean = mean
        self.eig = eig

        proj_rect = (eig)@(projs[:2])

        self.y_ref = np.mean(proj_rect[1])
        self.x_ref, _= (TEST_H-(105))*eig@((self.CM@np.array([self.axisCenter[0],0,1]))[:2])


        xlims = (np.min(x), np.max(x))
        f = self._computeParallelLine(*(np.mean(points[:2], axis=1)))

        return xlims, eig, f

    def calc_heights(self, mask, filter=True):

        xmin, _ = self.xlims

        xcenter, zcenter = self.axisCenter

        y, x = np.nonzero(mask)
        piece_points = np.vstack((x, y)).astype(np.float32)
        piece_points = np.vstack((piece_points, np.ones_like(x)))

        # piece_points = np.swapaxes(piece_points,0,1)

        # pdb.set_trace()
        projected_piece_points = self.CM@piece_points
        projected_piece_points = projected_piece_points[:2]
        projected_piece_points = (self.eig)@projected_piece_points
        xh, yh = projected_piece_points

        z = (TEST_H - self.tanAlfa*self.y_ref)/(1-self.tanAlfa*yh)

        x = +xh*z - self.x_ref
        h = TEST_H - z

        # projected_piece_points[1, :] *= self.heightFactor
        # projected_piece_points[0, :] /= self.ppcm

        if filter:
            x, heights = projected_piece_points
            inds = np.argsort(x)
            x = x[inds]
            heights = heights[inds]
            x = x[heights > 2]
            heights = heights[heights > 2]

            # x = (31.47-heights)*x/31.47
            heights -= zcenter
            return x, 10*np.ones_like(heights)

        return x, h-zcenter

    def perpLine(self, x, y):
        return self._computePerpLine(x, y)[0]

    def _computePerpLine(self, x, y):
        return lineFromVec(self.eig[0], x, y)

    def _computeParallelLine(self, x, y):
        return lineFromVec(self.eig[1], x, y)

    def draw_refLine(self, im,
                     color=(0, 0, 255),
                     width=8):
        x1, x2 = self.xlims
        y1, y2 = self.f(x1), self.f(x2)
        cv2.line(im, (int(x1), int(y1)), (int(x2), int(y2)),
                 color,
                 width)

    def linePoints(self, samples=100, asInt=True):
        x1, x2 = self.xlims
        px = np.linspace(x1, x2, samples)
        py = self.f(px)

        if asInt:
            points = np.round(np.array((px, py)))
            return points.T.astype(np.int32)
        else:
            points = np.array((px, py))
            return points.T

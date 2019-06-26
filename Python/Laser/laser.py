import cv2
import os
import matplotlib.pyplot as plt
import argparse
import json
import numpy as np

from PieceScanner import PieceScanner

REF_PHOTO = "/home/estudos/Pictures/Projeto2/TesteLaser/ref.jpg"
PIECE_PHOTO = "/home/estudos/Pictures/Projeto2/TesteLaser/inclinadoBorr.jpg"

# medida de um objeto na vida real e em uma imagem
PIXELS_PER_CM = 29

# tangente do angulo do laser com a superficie de ref.
TAN_LASER_ANGLE = 26.2/23


PLOT_EACH = False

def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser(description="Shows the results for images")
    ap.add_argument("reference", help="filepath of the ref. picture to use",
                    )
    ap.add_argument("pieces", nargs='+',
                    help="filepath of the pictures to run calculations on",
                    )
    ap.add_argument("--ppcm", type=float, help="Pixels per cm on the pictures",
                    default=PIXELS_PER_CM)
    return ap.parse_args()


def nothing(x):
    pass


def meanFilter(vec, w=2):
    v = vec
    for i in range(w, v.shape[0]-w):
        block = v[i-w:i+w+1]
        m = np.mean(block, dtype=np.float32)
        v[i] = m
    return v


if __name__ == "__main__":
    args = parseArgs()

    ref_im = cv2.imread(args.reference)

    scanner = PieceScanner(ppcm=PIXELS_PER_CM,
                           tanLaserAngle=TAN_LASER_ANGLE,
                           axisCenter=(346, 7.5))
    scanner.init_reference(ref_im)
    scanner.show_reference()

    for piece in args.pieces:
        piece_im = cv2.imread(piece)

        angle = os.path.splitext(piece)[0].split("pic")[-1]
        angle = np.pi*float(angle)/180
        x, heights = scanner.add_view(piece_im, angle)

        if PLOT_EACH:
            fig, axs = plt.subplots(1, 2)
            axs[0].imshow(piece_im)
            axs[0].set_title(angle)
            axs[1].plot(x, heights, 'b+')
            plt.show()

    points = scanner.get_piece()
    plt.figure()
    plt.plot(*points, 'go')
    plt.show()

    angles = (np.arctan2(points[0, :], points[1, :]))

    samples = 720
    dtheta = 2*np.pi/samples

    xp, yp = points
    points_filter = np.empty(points.shape)

    for i, a in enumerate(np.linspace(-np.pi, np.pi, samples)):

        in_range = np.bitwise_and(angles>= a, angles < a+dtheta)
        size = in_range.nonzero()[0].size

        xf = xp[in_range].sum()/size
        yf = yp[in_range].sum()/size
        points_filter[:,i] = np.array([xf,yf])

    plt.figure()
    plt.plot(*points_filter, 'go')
    plt.show()


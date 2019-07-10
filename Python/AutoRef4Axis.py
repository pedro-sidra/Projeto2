import cv2
import numpy as np

import FourthAxis.choosePieceRotationGUI as GUI
import Laser.laser as L
from FourthAxis.PictureAngleRelation.getPicForAngle import getPicsForAngles
from glob import glob

PLOT_EACH = False

#getPicsForAngles()

reference = "./ref.png"
pieces = glob("./OutputForAlgo/pic*")
L.calc4Axis(reference, pieces, PLOT_EACH)

GUI.getChosenPieceRotation(piece_img_file="fig.png", img_size=520)

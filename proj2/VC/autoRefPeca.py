import sys


import proj2.VC.shapedetect as shapedetect
from proj2.GCodeGenerator.GCodeGenerator import *

import argparse
import numpy as np
import time
import pdb
import cv2


# Teste de comunicacao com o Mach3!

# Ideia: este programa escreve um cod. G com uma coordenada,
# espera o Mach3 executar esse codigo e chegar ate a coordenada,
# e entao escreve outro codigo G para voltar pra posicao inicial

# This is a huge number
HUGENUMBER = 10000000

def waitForOK():
    receivedOk = False
    while not receivedOk:
        with open('fromMach3.txt', 'r') as fFromMach3:
            text = fFromMach3.readline()
            print('text ' + text)
            time.sleep(0.3)
        if text == 'ok\n':
            receivedOk = True
            open('fromMach3.txt', 'w').close()


def sendOK():
    with open('toMach3.txt', 'w') as fToMach3:
        fToMach3.write('ok')


def sendDone():
    with open('toMach3.txt', 'w') as fToMach3:
        fToMach3.write('exit')


def clearOK():
    open('toMach3.txt', 'w').close()


def waitForMach3():
    sendOK()
    waitForOK()
    clearOK()


# Comunicacao feita com arquivos de texto (aham...)
def takePicturesWithMachine(picturePositions, desiredFeedRate=500, device: int = None):
    # gerador de codigo G (clauser <3)
    gc = GCodeGenerator(5)
    if device is None:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(device)

    # initialize empty vector for the pictures
    picturesTaken = []

    # Clean up the communications
    open('fromMach3.txt', 'w').close()
    clearOK()

    # For each picture position...
    for pos in picturePositions:
        # Clear the file, set the code up and move to the position
        gc.cleanFile()
        gc.getInitialCode()
        gc.moveLinear(pos, feed_rate=desiredFeedRate)
        gc.insertNewLine()

        # Wait for mach3 to execute the desired movement
        waitForMach3()

        # Take a picture and append to the array
        _, picture = cap.read()
        picturesTaken.append(picture)

    return picturesTaken


def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--device", required=False, type=int,
                    default=0, help="device to use, int")
    ap.add_argument("--loadpics", action='store_true')
    args = vars(ap.parse_args())
    return args


def stitchImages(arrayOfImages, gambiarra: bool = False):
    if gambiarra:
        return np.concatenate(arrayOfImages, axis=0)
    else:
        stitcher = cv2.createStitcher(False)
        return stitcher.stitch(arrayOfImages)[1]


def findRelativeWorkpiecePosition(workpiece, reference):
    relativePosition = 100000
    bestWPoint = None
    bestRPoint = None

    for workpiecePoint in workpiece:
        for referencePoint in reference:
            newRelativePosition = (workpiecePoint - referencePoint)
            if (np.linalg.norm(newRelativePosition) < np.linalg.norm(relativePosition)):
                relativePosition = newRelativePosition
                bestWPoint = workpiecePoint
                bestRPoint = referencePoint

    return (relativePosition,
            bestWPoint,
            bestRPoint)

def readSavedTableImages():
    return [cv2.imread("mesa0.TIFF"), cv2.imread("mesa1.TIFF")]


def main():
    # Parse command line args and store them in a dict
    args = parseArgs()

    # Points to move the machine and take pictures
    # (Defines the number os pictures as well)
    PICTURE_POINTS = [
        Point(166, 300, 0),
        Point(440, 300, 0)
    ]
    # (When testing at home)
#    PICTURE_POINTS = [
#        Point(10,10,0),
#        Point(0,0,0),
#    ]
  
    # Calibrated points on the extremities of the reference tags
    PIECE_POINTS =[
        np.array((28.7,6.78)),
        np.array((425.1,0.62))
    ]

    # If the user requested to load images, read them
    # otherwise, take the pictures with the machine and write tem to mesa{0..n}
    if args['loadpics']:
        pictures = readSavedTableImages()
    else:
        pictures = takePicturesWithMachine(PICTURE_POINTS, device=args["device"])
        for num, pic in enumerate(pictures):
            cv2.imwrite("mesa"+str(num)+".TIFF", pic)

    # For each pictue, gets ref and piece contours
    # Chooses the pair that has the least distance from ref to piece
    # (RefPieceLen contains the tuple (ref, piece, lenght of distance) for each image)
    refs=[]
    pieces=[]
    chosenPictureidx = None
    minDist = None


    for i, pic in enumerate(pictures):
        print("Calibrate Reference:")
        ref = shapedetect.callibAndGetPiece(pic, 
                                            {"type": "hsv", "block": 3}, 
                                            paramsFile="refHSV.txt")
        print("Calibrate piece:")
        piece = shapedetect.callibAndGetPiece(pic,
                                              {"type": "hsv", "block": 3}, 
                                              paramsFile="pieceHSV.txt")

        if ref is not None and piece is not None:
            relPosPixels, pwork, pref = findRelativeWorkpiecePosition(workpiece=piece, reference=ref)
            dist = np.linalg.norm(relPosPixels)
        else:
            dist = None

        if dist is not None:
            if minDist is None or dist < minDist:
                minDist = dist
                chosenPictureidx = i

        refs.append(ref)
        pieces.append(piece)

    # Finds ref and piece such that norm(relPos) is minimum
    # (this means: minimum lenght of relPosPixels)
    # TODO: urgently make this more readable, its 2AM right now
    ref, piece, realRefPoint = refs[chosenPictureidx], pieces[chosenPictureidx], PIECE_POINTS[chosenPictureidx]

    pieceAngle = shapedetect.getAngle(piece, pwork, stitched)
    print("Angle: {:2f}".format(pieceAngle))
    
    refWidthReal = 35
    refHeightReal = 35

    p, size, angle = cv2.minAreaRect(ref)

    mmPerPixel = (refWidthReal / size[0] + refHeightReal / size[1])/2

    if ref is not None and piece is not None:
        relPosPixels, pwork, pref = findRelativeWorkpiecePosition(workpiece=piece, reference=ref)

        # cv2.line(stitched, (pwork[0],pwork[1]), (pref[0],pref[1]), (255,0,0) ,1 )
        # cv2.imshow("Posicao Realtiva",stitched)

        gc = GCodeGenerator(5)

        relX = relPosPixels[0][1] * mmPerPixel
        relY = relPosPixels[0][0] * mmPerPixel

        Xref = relX + realRefPoint[0]
        Yref = relY + realRefPoint[1]


        # maquina.vaiPra(x,y,z)
        # maquina.zeraRef()
        # maquina.rotacionaSCM(angulo)
        gc.cleanFile()
        gc.getInitialCode()
        gc.moveLinear(Point(Xref, Yref, 0))
        gc.setReference(Point(0, 0, 0))
        gc.rotateCoordinateSystem(pieceAngle)
        gc.insertNewLine()

        waitForMach3()

    else:
        print("NAO DEU")


if __name__ == "__main__":
    main()

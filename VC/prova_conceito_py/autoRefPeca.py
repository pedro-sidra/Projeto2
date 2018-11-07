from GCodeGenerator.GCodeGenerator import *
from . import shapedetect
import argparse
import numpy as np
import time
import cv2


# Teste de comunicacao com o Mach3!

# Ideia: este programa escreve um cod. G com uma coordenada,
# espera o Mach3 executar esse codigo e chegar ate a coordenada,
# e entao escreve outro codigo G para voltar pra posicao inicial

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


def main():
    args = parseArgs()
    print(args)

    picturePoints = [
        Point(166, 300, 0),
        Point(440, 300, 0)
    ]

    pictures = takePicturesWithMachine(picturePoints, device=args["device"])

    # for pic in pictures:
    # cv2.imshow("Pic", pic)
    # cv2.waitKey()

    stitched = stitchImages(pictures, gambiarra=True)

    # cv2.imshow("Result of Stitch", stitched)
    # cv2.waitKey()

    ref = shapedetect.callibAndGetPiece(stitched, {"type": "hsv", "block": 3})
    piece = shapedetect.callibAndGetPiece(stitched, {"type": "hsv", "block": 3})

    print(ref)
    print(piece)

    refWidthReal = 5
    refHeightReal = 3.8

    p, size, angle = cv2.minAreaRect(ref)

    mmPerPixel = (refWidthReal / size[0] + refHeightReal / size[1]) * 10 / 2

    if ref is not None and piece is not None:
        relPosPixels, pwork, pref = findRelativeWorkpiecePosition(workpiece=piece, reference=ref)

        # cv2.line(stitched, (pwork[0],pwork[1]), (pref[0],pref[1]), (255,0,0) ,1 )
        # cv2.imshow("Posicao Realtiva",stitched)

        gc = GCodeGenerator(5)
        gc.getInitialCode()
        gc.moveLinear(Point(30, 60, 0))
        gc.insertNewLine()

        waitForMach3()

        gc.cleanFile()
        gc.getInitialCode()
        gc.enterRelativeMode()
        print(relPosPixels)
        relX = relPosPixels[0][1] * mmPerPixel
        relY = relPosPixels[0][0] * mmPerPixel
        gc.moveLinear(Point(relX, relY, 0))
        gc.insertNewLine()

        waitForMach3()

    else:
        print("NAO DEU")


if __name__ == "__main__":
    main()

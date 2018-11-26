import numpy as np
import cv2

USE_CORNER_DETECTION = False


def findCorner(img):
    # Converte para grayscale se necessário
    if img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    gray = np.float32(gray)

    # Obtém os cantos
    dst = cv2.cornerHarris(gray, 5, 5, 0.04)
    dst = cv2.dilate(dst, None)
    ret, dst = cv2.threshold(dst, 0.01 * dst.max(), 255, 0)
    dst = np.uint8(dst)

    # Encontra os centróides dos cantos obtidos
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

    # A partir dos centróides, obtém um canto 
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria)
    # Desenha os cantos
    # res = np.hstack((centroids,corners))
    # res = np.int0(res)
    # image[res[:,1],res[:,0]]=[0,0,255]
    # image[res[:,3],res[:,2]] = [0,255,0]

    return corners


# Obtém uma máscara que separa objetos se baseando na sua cor
def getArea(img, lower_bound, upper_bound):
    # Converte a imagem para HSV, para filtrar mais facilmente
    imageHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Cria uma máscara com os limites definidos
    mask = cv2.inRange(imageHSV, lower_bound, upper_bound)

    # Aplica operações de abertura e fechamento na máscara 
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


# Encontra uma peça genérica
def findPiece(img, margin, lower_bound, upper_bound):
    # Obtém o filtro

    thresh = getArea(img, lower_bound, upper_bound)

    # Obtém os contornos presentes na máscara
    _, contoursBlack, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    areaWorkpiece = 0
    # Itera os contornos obtidos

    local_workpiece = None
    for i in range(0, len(contoursBlack)):
        # Aplica uma aproximação polinomial nos contornos
        polyApprox = cv2.approxPolyDP(contoursBlack[i], 8, True)

        # Assume-se que a peça é um quadrilátero
        area = cv2.contourArea(polyApprox)
        # Assume-se que a peça será o objeto com maior área detectado
        if area > areaWorkpiece:
            local_workpiece = polyApprox
            areaWorkpiece = cv2.contourArea(local_workpiece)
    xmin = min(local_workpiece[:, 0, 0]) - margin
    xmax = max(local_workpiece[:, 0, 0]) + margin
    ymin = min(local_workpiece[:, 0, 1]) - margin
    ymax = max(local_workpiece[:, 0, 1]) + margin

    workpieceImage = img[ymin:ymax, xmin:xmax]

    # cv2.drawContours(image, [local_workpiece], -1, (0,255,0), 1)
    if USE_CORNER_DETECTION:
        corners = findCorner(workpieceImage)
        corners[:, 0] += xmin
        corners[:, 1] += ymin
    else:
        corners = local_workpiece[:, 0, :]

    return corners


# Encontra a menor distância entre os vértices da peça e da referência
def findRelativeWorkpiecePosition(param_workpiece, ref):
    relPosition = 100000
    bestWPoint = None
    bestRPoint = None
    for workpiecePoint in param_workpiece:
        for referencePoint in ref:
            newRelativePosition = (workpiecePoint - referencePoint)
            if np.linalg.norm(newRelativePosition) < np.linalg.norm(relPosition):
                relPosition = newRelativePosition
                bestWPoint = workpiecePoint
                bestRPoint = referencePoint

    return (relPosition,
            bestWPoint,
            bestRPoint)


# MAIN

lower_piece = np.array([0, 0, 0])
upper_piece = np.array([28, 255, 73])

lower_reference = np.array([0, 157, 87])
upper_reference = np.array([15, 255, 255])

image = cv2.imread("img.jpeg", cv2.IMREAD_COLOR)

workpiece = findPiece(image, 20, lower_piece, upper_piece)
reference = findPiece(image, 20, lower_reference, upper_reference)

referenceWidth = 180.0
referenceHeight = 130.0

cmPerPixel = (5.0 / referenceWidth + 7.0 / referenceHeight) / 2
print(workpiece)
print(reference)
relativePosition, P1, P2 = findRelativeWorkpiecePosition(workpiece, reference)
print(relativePosition[0])
workpieceDistance = cmPerPixel * np.linalg.norm(relativePosition, 2)

cv2.putText(image, "Distancia medida: " + str(workpieceDistance) + " cm", (10, 600), cv2.FONT_HERSHEY_SIMPLEX, 1,
            (255, 255, 255))
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

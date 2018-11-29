import cv2
import json
import numpy as np
from collections import OrderedDict
import os
import math

import argparse

# ShapeDetect

# For testing binarization algorithms to detect shapes

# Ta tudo em ingles mas aqui vai ser br krl
# TUTORIAL PRA QUEM FOR TESTAR:

# para chamar o programa na linha de comando de forma bonita:
# python3 shapedetect.py -i [caminho pra imagem] -t [tipo de algoritmo] -b [tamanho do bloco]

# Me recusei a botar as opcoes no codigo, mas se quiser fazer hardcode:
HARDCODEFEIO = False


# Muda essa variavel pra True e da um ctrl+F pra encontrar a prox ocorrencia dela,
# dai muda as coisas no dedo
# (deixei facil pq n sabia se ia funcionar no windows, mas nao faz isso pfv)

# Parametros:
# -i caminho pra sua imagem 
# -t tipo do algoritmo, um desses:
#       ada: Threshold adaptativo. Faz uma media os pixels ao redor, numa janela determinada
#            pelo parametro blocksize. Se media-Cval > 0, a saida eh 1, senao eh 0
#       bin: Threshold burro padrao. Saida eh 1 se intensidade > thresh, senao eh 0
#       canny: Filtro de borda, tem q calibrar dois parametros q eu n entendo mt bem
#               se botar -t canny, bota tambem -b 1 (operacao morfologica fode o canny)
#       hsv: Saida eh 1 se os valores HSV estiverem dentro dos definidos
#       hsvneg: igual ao hsv, mas o range do H eh negado (saida eh 1 se estiver fora do range q vc calibrar)
#               isso eh pra lidar com o vermelho. Botar o high perto de 180 e o low perto de 0 pra 
#               detectar vermelho
# -b tamanho do bloco usado na morfologia. Geralmente 3, 5 ou 7 (se vc botar um numero par, vai dar merda)


def nothing(x):
    pass


# Return a dict containing the necessary params for each type
# of binarization defined
# the initial value is the max range of the param (after initialization 
# the value will be the current value of the param)
def getParamDict(args):
    if args["type"] == "ada":
        return OrderedDict([('blockSize', 1000), ('Cval', 255)])
    elif args["type"] == "canny":
        return OrderedDict([('thresh1', 500), ('thresh2', 500)])
    elif args["type"] == "bin":
        return OrderedDict([('thresh', 255)])
    elif args["type"] == "otsu":
        return OrderedDict([])
    elif args["type"] == "hsv":
        return OrderedDict([('highH', 180), ('lowH', 180), ('highS', 255), ('lowS', 255), ('highV', 255), ('lowV', 255)])
    elif args["type"] == "hsvneg":
        return OrderedDict([('highHNeg', 180), ('lowHNeg', 180), ('highS', 255), ('lowS', 255), ('highV', 255), ('lowV', 255)])
    else:
        return OrderedDict([('blockSize', 300), ('Cval', 255)])


# From the parameters passed, create appropriate trackbars
def createBinarizationTrackbars(args):
    # Get the necessary params in a dict
    params = getParamDict(args)

    # Iterate over the params and create a trackbar for each
    for paramName, value in params.items():
        cv2.createTrackbar(paramName, 'Mask', 1, value, nothing)

def setBinarizationParams(params):

    # Iterate over the params and create a trackbar for each
    for paramName, value in params.items():
        cv2.setTrackbarPos(paramName, 'Mask', int(value))

def getBinarizationParams(args):
    # Get the params in a dict
    params = getParamDict(args)

    # For each param, get its value from the trackbar
    for key, value in params.items():
        params[key] = cv2.getTrackbarPos(key, 'Mask')

    return params

def isPerpendicular(angle1,angle2, tol):
    return not(abs(angle1-angle2)<90-tol or abs(angle1-angle2)>90+tol)

# Retorna o ângulo de um contorno
def getAngle(contour, workpiece, image):

    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints (rect)

    origin = []
    dist = 100000
    i=0
    for boxes in box: # Encontra a origem do sistema de coordenadas
        if (np.linalg.norm(boxes-workpiece[0])<dist):
            dist = np.linalg.norm(boxes-workpiece[0])
            index = i
            i+=1
            origin = boxes        

    box = np.delete(box,index,0)    
    lineAngles = []
    for boxes in box:
        lineAngles.append(-(math.atan2(boxes[1]-origin[1],boxes[0]-origin[0]))*180/math.pi)
        
        #cv2.line(image, (origin[0],origin[1]), (boxes[0],boxes[1]), (0,255,255) ,1 )
    
    if isPerpendicular(lineAngles[1],lineAngles[0],5):
        del lineAngles[2]
    elif isPerpendicular(lineAngles[2],lineAngles[0],5):
        del lineAngles[1]
    elif isPerpendicular(lineAngles[2],lineAngles[1],5):
        del lineAngles[0]
    #verifica se o primeiro valor é o eixo y
    lineAngles = np.array(lineAngles)
    if(lineAngles[1]-lineAngles[0])<0:
        angle = lineAngles[0]
    else:   
        angle = lineAngles[1] 
  
    return angle





# Obtém uma máscara que separa objetos se baseando na sua cor
def getArea(image, lower_bound, upper_bound):
    # Converte a imagem para HSV, para filtrar mais facilmente
    imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Cria uma máscara com os limites definidos
    mask = cv2.inRange(imageHSV, lower_bound, upper_bound)

    # Aplica operações de abertura e fechamento na máscara 
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


# Obtem mascara de acordo com as opcoes do programa
def getMaskFromOptions(args, params, image):

    if args["type"] == "ada":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.adaptiveThreshold(
            image, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            2 * params['blockSize'] + 3,
            params['Cval'])

    elif args["type"] == "canny":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Canny(cv2.GaussianBlur(image, (5, 5), 0),
                         params['thresh1'],
                         params['thresh2'])
    elif args["type"] == "bin":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.threshold(image, params['thresh'], 255, cv2.THRESH_BINARY)[1]
    elif args["type"] == "otsu":
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    elif args["type"] == "hsv":
        # Convert to HSV
        imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create range arrays
        lowRange = np.array([params['lowH'], params['lowS'], params['lowV']])
        highRange = np.array([params['highH'], params['highS'], params['highV']])

        # Return what is inside the HSV range
        return cv2.inRange(imageHSV, lowRange, highRange)

    elif args["type"] == "hsvneg":

        # Convert to HSV
        imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create range arrays for first case
        lowRange = np.array([0, params['lowS'], params['lowV']])
        highRange = np.array([params['lowHNeg'], params['highS'], params['highV']])
        # First mask contains H values lower than lowHNeg
        mask1 = cv2.inRange(imageHSV, lowRange, highRange)

        # Create range arrays for second case
        lowRange = np.array([params['highHNeg'], params['lowS'], params['lowV']])
        highRange = np.array([180, params['highS'], params['highV']])
        # Second mask contains H values higher than highHNeg
        mask2 = cv2.inRange(imageHSV, lowRange, highRange)

        # The return is anything in either mask
        return cv2.bitwise_or(mask1, mask2)
    else:
        return cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV, 2 * params['blockSize'] + 3, params['Cval'])


def parseArgs():
    # Parse arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=False,
                    help="path to the input image")
    ap.add_argument("-d", "--device", required=False,
                    type=int, default=0,
                    help="device to use")
    ap.add_argument("-t", "--type", required=False,
                    default="ada",
                    help="type of binarization")
    ap.add_argument("-b", "--block", required=False,
                    type=int, default=5,
                    help="size of the block in morph operations")
    args = vars(ap.parse_args())

    if HARDCODEFEIO:
        args["type"] = 'ada'
        args["image"] = '/home/freitas/Downloads/test.jpeg'
        args["block"] = 3
    return args


def morphCloseThenOpen(args, mask):
    kernel = np.ones((args['block'], args['block']), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def findCorner(image):
    # Converte para grayscale se necessário
    if image.shape[2] == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

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


# Encontra uma peça genérica
USE_CORNER_DETECTION = False


def findPiece(mask, margin=None):
    # Obtém os contornos presentes na máscara
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    areaWorkpiece = 0
    # Itera os contornos obtidos

    workpiece = None

    for contour in contours:
        # Aplica uma aproximação polinomial nos contornos
        polyApprox = cv2.approxPolyDP(contour, 8, True)

        # Assume-se que a peça é um quadrilátero
        area = cv2.contourArea(polyApprox)
        # Assume-se que a peça será o objeto com maior área detectado
        if area > areaWorkpiece:
            workpiece = polyApprox
            areaWorkpiece = cv2.contourArea(workpiece)

    if USE_CORNER_DETECTION:
        xmin = min(workpiece[:, 0, 0]) - margin
        xmax = max(workpiece[:, 0, 0]) + margin
        ymin = min(workpiece[:, 0, 1]) - margin
        ymax = max(workpiece[:, 0, 1]) + margin

        workpieceImage = mask[ymin:ymax, xmin:xmax]
        corners = findCorner(workpieceImage)
        corners[:, 0] += xmin
        corners[:, 1] += ymin
        return corners
    else:
        return workpiece


def callibAndGetPiece(image, args, paramsFile=None):
    # Create trackbars window
    cv2.namedWindow('Mask', cv2.WINDOW_AUTOSIZE)
    createBinarizationTrackbars(args)

    if paramsFile is not None and os.path.isfile(paramsFile):
        with open(paramsFile, 'r') as f:
            text = f.read()
            params = json.loads(text)
        setBinarizationParams(params)
    while True:
        params = getBinarizationParams(args)

        mask = getMaskFromOptions(args, params, image)

        mask = morphCloseThenOpen(args, mask)

        workpiece = findPiece(mask)
        drawImage = image.copy()
        if workpiece is not None:
            cv2.drawContours(drawImage, [workpiece], -1, (0, 255, 0), 1)
        cv2.imshow("Mask", mask)
        cv2.imshow("Image", drawImage)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    if paramsFile is not None:
        params = getBinarizationParams(args)
        with open(paramsFile,'w') as f:
            f.write(json.dumps(params))

    return workpiece


def main():
    # Init argument parser
    args = parseArgs()

    # Create trackbars window
    cv2.namedWindow('Mask', cv2.WINDOW_AUTOSIZE)
    createBinarizationTrackbars(args)

    # Read image
    image = cv2.imread(args["image"], cv2.IMREAD_COLOR)

    while True:
        mask = getMaskFromOptions(args, image)
        mask = morphCloseThenOpen(args, mask)

        workpiece = findPiece(mask)
        drawImage = image.copy()
        if workpiece is not None:
            cv2.drawContours(drawImage, [workpiece], -1, (0, 255, 0), 1)
            print(workpiece[0][0][0])
            rect = cv2.minAreaRect(workpiece)
            print(rect)
        cv2.imshow("Mask", mask)
        cv2.imshow("Image", drawImage)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break


if __name__ == "__main__":
    main()

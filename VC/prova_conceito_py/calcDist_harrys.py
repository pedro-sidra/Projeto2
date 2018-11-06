import numpy as np
import cv2

USE_CORNER_DETECTION=False

def getAngle(contour):
    rect = cv2.minAreaRect(contour)

    print(rect[2])
    return rect

def findCorner(image):
    # Converte para grayscale se necessário
    if image.shape[2] == 3:
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    gray = np.float32(gray)
    
    # Obtém os cantos
    dst = cv2.cornerHarris(gray,5,5,0.04)
    dst = cv2.dilate(dst,None)
    ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
    dst = np.uint8(dst)

    # Encontra os centróides dos cantos obtidos
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

    # A partir dos centróides, obtém um canto 
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
    # Desenha os cantos
    #res = np.hstack((centroids,corners))
    #res = np.int0(res)
    #image[res[:,1],res[:,0]]=[0,0,255]
    #image[res[:,3],res[:,2]] = [0,255,0]

    return corners
        
# Obtém uma máscara que separa objetos se baseando na sua cor
def getArea(image, lower_bound, upper_bound):

    # Converte a imagem para HSV, para filtrar mais facilmente
    imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Cria uma máscara com os limites definidos
    mask = cv2.inRange(imageHSV, lower_bound, upper_bound)
    
    # Aplica operações de abertura e fechamento na máscara 
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

# Encontra uma peça genérica 
def findPiece(image, margin, lower_bound, upper_bound):
    # Obtém o filtro
    
    thresh = getArea(image, lower_bound, upper_bound)
    
    # Obtém os contornos presentes na máscara
    _ , contoursBlack, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    areaWorkpiece = 0
    # Itera os contornos obtidos

    for i in range(0, len(contoursBlack)):
        # Aplica uma aproximação polinomial nos contornos
        polyApprox = cv2.approxPolyDP(contoursBlack[i],8,True)
        
        # Assume-se que a peça é um quadrilátero
        area = cv2.contourArea(polyApprox)
        # Assume-se que a peça será o objeto com maior área detectado
        if(area>areaWorkpiece):
            workpiece = polyApprox
            areaWorkpiece = cv2.contourArea(workpiece)
    xmin = min(workpiece[:,0,0])-margin
    xmax = max(workpiece[:,0,0])+margin
    ymin = min(workpiece[:,0,1])-margin
    ymax = max(workpiece[:,0,1])+margin

    workpieceImage = image[ymin:ymax,xmin:xmax]
    
    #cv2.drawContours(image, [workpiece], -1, (0,255,0), 1)
    if USE_CORNER_DETECTION:
        corners = findCorner(workpieceImage)
        corners[:,0]+=xmin
        corners[:,1]+=ymin
    else:
        corners=workpiece[:,0,:]

    
    return corners


# Encontra a menor distância entre os vértices da peça e da referência
def findRelativeWorkpiecePosition(workpiece, reference):
    relativePosition=100000
    bestI=0
    bestJ=0
    for i in range((len(workpiece))):
        for j in range((len(reference))):
            newRelativePosition = (workpiece[i]-reference[j])
            if(np.linalg.norm(newRelativePosition)<np.linalg.norm(relativePosition)):
                relativePosition = newRelativePosition
                bestI=i
                bestJ=j
            
    cv2.line(image, (workpiece[bestI,0],workpiece[bestI,1]),(reference[bestJ,0],reference[bestJ,1]), (255,0,0) ,1 )
    
    return relativePosition


#MAIN

lower_piece= np.array([0,0,0])
upper_piece = np.array([28,255,73])

lower_reference = np.array([0,157,87])
upper_reference = np.array([15,255,255])

image= cv2.imread('/home/hanel/Projeto2/VC/prova_conceito_py/img.jpeg',cv2.IMREAD_COLOR)

workpiece = findPiece(image, 20, lower_piece, upper_piece)
reference = findPiece(image, 20, lower_reference, upper_reference)
print(workpiece)
rect = getAngle(workpiece)
box = cv2.boxPoints(rect)
box = np.int0(box)

cv2.drawContours(image,[box],-1,(0,0,255),1)

referenceWidth = 180.0
referenceHeight = 130.0

cmPerPixel = (5.0/referenceWidth + 7.0/referenceHeight)/2
relativePosition = findRelativeWorkpiecePosition(workpiece, reference)
workpieceDistance = cmPerPixel*np.linalg.norm(relativePosition,2)

cv2.putText(image, "Distancia medida: " + str(workpieceDistance)+ " cm", (10,600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
cv2.imshow('image',image)
cv2.waitKey(0)
cv2.destroyAllWindows() 

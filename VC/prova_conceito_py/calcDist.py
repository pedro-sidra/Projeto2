import numpy as np
import cv2

# Obtém uma máscara que separa os objetos vermelhos (objeto de referência)
def getRedArea(image):
    # Define os limites para filtragem do vermelho
    lower_red = np.array([0,100,100])
    upper_red = np.array([18,255,255])

    # Converte a imagem para HSV, para filtrar mais facilmente
    imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Cria uma máscara com os limites definidos
    mask = cv2.inRange(imageHSV, lower_red, upper_red)
    
    # Aplica operações de abertura e fechamento na máscara 
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask


# Obtém uma máscara que separá os objetos pretos (peça)
def getBlackArea(image):
    # Converte a imagem para Grayscale e aplica uma operação de Threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, threshBlack, 255, cv2.THRESH_BINARY)
    
    # Aplica operações de abertura e fechamento na máscara 
    kernel = np.ones((5,5),np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    return thresh


# Encontra o objeto de referência
def findReference(image):
    # Obtém o filtro para objetos vermelhos
    thresh = getRedArea(image)
    
    # Obtém os contornos presentes na máscara
    _ , contoursRed, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
   
    # Encontra o menor retângulo que consegue envolver o contorno
    # rect possui a forma: ( centro (x,y), (largura, altura), ângulo de rotação)
    rect = cv2.minAreaRect(contoursRed[0])

    # Converte rect para um vetor com os 4 vértices do retângulo
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # Desenha o retângulo na imagem original
    cv2.drawContours(image,[box],0,(0,0,255),1)
    
    return rect


# Encontra a peça
def findPiece(image):
    # Obtém o filtro para objetos pretos
    thresh = getBlackArea(image)
    
    # Obtém os contornos presentes na máscara
    _ , contoursBlack, _ = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    areaWorkpiece = 0
    
    # Itera os contornos obtidos
    for i in range(0, len(contoursBlack)):
        # Aplica uma aproximação polinomial nos contornos
        polyApprox = cv2.approxPolyDP(contoursBlack[i],8,True)
        # Assume-se que a peça é um quadrilátero
        if len(polyApprox) is 4:
            area = cv2.contourArea(polyApprox)
            # Assume-se que a peça será o objeto com maior área detectado
            if(area>areaWorkpiece):
                workpiece = polyApprox
                areaWorkpiece = cv2.contourArea(workpiece)
    
    cv2.drawContours(image, [workpiece], -1, (0,255,0), 1)    

    return workpiece

# Encontra a distância entre o vértice inferior direito da referência e
# o vértice superior esquerdo da peça, em pixels
def findRelativeWorkpiecePosition(workpiece, reference):
    x_pos=[]
    y_pos=[]

    # Itera sob as coordenadas do vetor workpiece e separa as coordenadas x e y
    for i in range(len(workpiece)):
        x_pos.append(workpiece[i][0][0])
        y_pos.append(workpiece[i][0][1])
    
    # Converte a referência da forma ( centro (x,y), (largura, altura), ângulo de rotação)
    # para a forma de um vetor com as coordenadas dos vértices
    reference = cv2.boxPoints(reference)
    reference = np.int0(reference)

    # Encontra a posição do vértice mais à esquerda da peça
    leftIndex = x_pos.index(min(x_pos))
    leftMost = [x_pos[leftIndex],y_pos[leftIndex]]

    # Sabe-se que o vértice de interesse está na posição 3 do vetor
    referencePoint = reference[3]

    relativePosition = leftMost-referencePoint
    cv2.line(image, (referencePoint[0],referencePoint[1]),(leftMost[0],leftMost[1]), (255,0,0) ,1 )
    return relativePosition

#MAIN

threshBlack = 40

image= cv2.imread('/home/hanel/VisualStudio/Python/Proj2/img.jpeg',cv2.IMREAD_COLOR)

workpiece = findPiece(image)
reference = findReference(image)
referenceWidth = reference[1][0]
referenceHeight = reference[1][1]

cmPerPixel = (5.0/referenceWidth + 7.0/referenceHeight)/2
relativePosition = findRelativeWorkpiecePosition(workpiece, reference)
workpieceDistance = cmPerPixel*np.linalg.norm(relativePosition,2)

cv2.putText(image, "Distancia medida: " + str(workpieceDistance)+ " cm", (10,600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255))
cv2.imshow('image',image)
cv2.waitKey(0)
cv2.destroyAllWindows()

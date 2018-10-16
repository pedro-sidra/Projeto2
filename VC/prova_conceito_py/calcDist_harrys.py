import numpy as np
import cv2

def findCorner(image):
    # Converte para grayscale se necessário
    if image.shape[2] == 3:
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    gray = np.float32(gray)
    
    # Obtém os cantos
    dst = cv2.cornerHarris(gray,2,3,0.04)
    dst = cv2.dilate(dst,None)
    ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
    dst = np.uint8(dst)

    # Encontra os centróides dos cantos obtidos
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

    # A partir dos centróides, obtém um canto 
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
    # Desenha os cantos
    res = np.hstack((centroids,corners))
    res = np.int0(res)
    image[res[:,1],res[:,0]]=[0,0,255]
    image[res[:,3],res[:,2]] = [0,255,0]

    return corners
        

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
def findPiece(image, margin):
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
    
    xmin = min(workpiece[:,0,0])-margin
    xmax = max(workpiece[:,0,0])+margin
    ymin = min(workpiece[:,0,1])-margin
    ymax = max(workpiece[:,0,1])+margin

    workpieceImage = image[ymin:ymax,xmin:xmax]
    
    #cv2.drawContours(image, [workpiece], -1, (0,255,0), 1)    
    corners = findCorner(workpieceImage)
    corners[:,0]+=xmin
    corners[:,1]+=ymin
    '''cv2.imshow('image',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows(workpieceImage)
    '''
    return corners

# Encontra a distância entre o vértice inferior direito da referência e
# o vértice superior esquerdo da peça, em pixels
def findRelativeWorkpiecePosition(workpiece, reference):
    
    x_pos=workpiece[:,0]
    y_pos=workpiece[:,1]

    
    # Converte a referência da forma ( centro (x,y), (largura, altura), ângulo de rotação)
    # para a forma de um vetor com as coordenadas dos vértices
    reference = cv2.boxPoints(reference)
    reference = np.int0(reference)

    # Encontra a posição do vértice mais à esquerda da peça
    leftIndex = np.argmin(x_pos)
    print(leftIndex)
    leftMost = workpiece[leftIndex]
    
    # Sabe-se que o vértice de interesse está na posição 3 do vetor
    referencePoint = reference[3]
    print(leftMost)
    print(referencePoint)
    relativePosition = (leftMost-referencePoint)
   
    cv2.line(image, (referencePoint[0],referencePoint[1]),(leftMost[0],leftMost[1]), (255,0,0) ,1 )
    return relativePosition

#MAIN

threshBlack = 40

image= cv2.imread('/home/hanel/Projeto2/VC/prova_conceito_py/img.jpeg',cv2.IMREAD_COLOR)

workpiece = findPiece(image, 20)
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

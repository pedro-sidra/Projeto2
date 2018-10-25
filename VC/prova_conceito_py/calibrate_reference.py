import cv2
import numpy as np

def nothing(x):
    pass


cv2.namedWindow('image')

# Criação das barras para calibração
cv2.createTrackbar('Low H','image',0,255,nothing)
cv2.createTrackbar('Low S','image',0,255,nothing)
cv2.createTrackbar('Low V','image',0,255,nothing)
cv2.createTrackbar('High H','image',0,255,nothing)
cv2.createTrackbar('High S','image',0,255,nothing)
cv2.createTrackbar('High V','image',0,255,nothing)

while(1):
    image= cv2.imread('/home/hanel/Projeto2/VC/prova_conceito_py/img.jpeg',cv2.IMREAD_COLOR)
    k = cv2.waitKey(1) & 0xFF
    
    if k == 27:
        break


    # Obtém os valores de todas as barras
    lowH = cv2.getTrackbarPos('Low H','image')
    lowS = cv2.getTrackbarPos('Low S','image')
    lowV = cv2.getTrackbarPos('Low V','image')
    highH = cv2.getTrackbarPos('High H','image')
    highS = cv2.getTrackbarPos('High S','image')
    highV = cv2.getTrackbarPos('High V','image')

    # Define os limites para os filtros
    lower_red = np.array([lowH,lowS,lowV])
    upper_red = np.array([highH,highS,highV])

    # Converte a imagem para HSV, para filtrar mais facilmente
    imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Cria uma máscara com os limites definidos
    mask = cv2.inRange(imageHSV, lower_red, upper_red)
    
    # Aplica operações de abertura e fechamento na máscara 
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    image = cv2.bitwise_and(image,image,mask = mask)
    cv2.imshow('image',image)
cv2.destroyAllWindows()
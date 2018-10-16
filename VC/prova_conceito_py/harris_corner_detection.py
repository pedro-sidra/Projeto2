import cv2
import numpy as np
import cv2
import numpy as np

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
    print (corners)
    # Desenha os cantos
    #res = np.hstack((centroids,corners))
    #res = np.int0(res)
    #image[res[:,1],res[:,0]]=[0,0,255]
    #image[res[:,3],res[:,2]] = [0,255,0]
    return corners
        

filename = 'square.png'
img = cv2.imread(filename)
findCorner(img)

cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
filename = 'square.png'
img = cv2.imread(filename)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# find Harris corners
gray = np.float32(gray)
dst = cv2.cornerHarris(gray,2,3,0.04)
dst = cv2.dilate(dst,None)
ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
dst = np.uint8(dst)

# find centroids
ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

# define the criteria to stop and refine the corners
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
print (corners)
# Now draw them
res = np.hstack((centroids,corners))
res = np.int0(res)
img[res[:,1],res[:,0]]=[0,0,255]
img[res[:,3],res[:,2]] = [0,255,0]

cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
import numpy as np
import cv2
class ImageLoader():
    def __init__(self, params_file, resize):
        self.resize = resize

        contents = np.load(params_file)
        cameraMatrix = contents['mtx']
        distCoeff = contents['dist']

        w,  h = resize
        self.optCameraMtx, self.roi = cv2.getOptimalNewCameraMatrix(
            cameraMatrix, distCoeff,
            (w, h), 0, (w, h))

        self.mapx, self.mapy = cv2.initUndistortRectifyMap(cameraMatrix, distCoeff,
                                                           None, self.optCameraMtx, (
                                                               w, h),
                                                           5)

    def get_mtx(self):
        return self.optCameraMtx
    def get_img(self,path):
        dst = cv2.imread(path)
        dst = cv2.resize(dst, self.resize)
        dst = cv2.remap(dst, self.mapx, self.mapy, cv2.INTER_LINEAR)
        x, y, w, h = self.roi
        dst = dst[y:y+h, x:x+w]
        return dst

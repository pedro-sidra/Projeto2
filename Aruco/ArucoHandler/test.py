from ArucoHandler import *

camera = NotebookCamera()
arc_handler = ArucoHandler()
imageToDetectMarkers = cv2.imread("paperMarker2.jpg")

[corn, ids, rejected] = arc_handler.detectMarkersInImage(imageToDetectMarkers)
[rvecs, tvecs, _objPoints] = arc_handler.estimateArucoPose(imageToDetectMarkers, corn, camera,)
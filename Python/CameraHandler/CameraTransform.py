"""This file defines functions to convert image pixels to spacial coordinates
and inversely, converts also spacial coordinates to image pixels."""


import numpy as np

M = np.load("camera_mtx.npy")

#Gets uv position from XY spacial coordinates and a given z height
def Get_uv(x,y,z):
    u,v=M*[x;y]/z
    return u,v

#Gets XY coordinates from pixel position(u,v) and a given z height
def Get_xy(u,v,z):
    x,y=np.linalg.inv(M)*[u;v]/z #inverse matrix
    return x,y




"""This file defines functions to convert image pixels to spacial coordinates
and inversely, converts also spacial coordinates to image pixels."""


import numpy as np

M = np.load("camera_mtx.npy")

#Gets uv position from XY spacial coordinates and a given z height
def Get_uv(x,y,z):
  P=np.array([[x],[y]])
    u,v=M@P/z
    return u,v

#Gets XY coordinates from pixel position(u,v) and a given z height
def Get_xy(u,v,z):
    P=np.array([[x],[y]])
    x,y=np.linalg.inv(M)@P/z #inverse matrix
    return x,y

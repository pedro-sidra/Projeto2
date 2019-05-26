"""This file defines the getTimedPictures function, which is responsible for taking many pictures and storing the
relation between the time and the respective picture in order to prepare a sequence of pictures."""

import os, shutil
from FourthAxis.CameraHandler import *
import time

# region Defined Constants

IS_SIMULATING_MACH3 = True
SIMULATION_SLEEP = 0.050

DEFAULT_N_OF_SAMPLE = 100
DEFAULT_FOLDER_OF_PICTURES = './TimedPictures'
DEFAULT_TIME_BETWEEN_PICS_S = 0.1

# endregion

def getTimedPictures(n_of_samples=DEFAULT_N_OF_SAMPLE,
                     time_bt_pics=DEFAULT_TIME_BETWEEN_PICS_S,
                     folder_of_pic=None) -> tuple:

    # Prepares Camera. It's possible to change here for a specific camera instead of using a generic CameraHandler.
    ch = CameraHandler()

    # region Prepares Mach3 simulation
    fMach3 = None
    if IS_SIMULATING_MACH3:
        fMach3 = open('./TimedAngles/angle.txt', mode='w', encoding='UTF-8', errors='ignore')
    # endregion

    # region Clean TimedPictures folder to avoid filling the HD in the future
    # Source of this part of the code:
    # https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder-in-python

    if folder_of_pic is None:
        folder_of_pic = DEFAULT_FOLDER_OF_PICTURES

    for the_file in os.listdir(folder_of_pic):
        file_path = os.path.join(folder_of_pic, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    # endregion

    # region Takes pictures and keeps timestamp in number of seconds since the epoch, as seconds
    listPic = []
    listTime = []
    lastSimulatedAngle = 0
    for idx in range(n_of_samples):

        if IS_SIMULATING_MACH3:
            ts = time.time()
            lastSimulatedAngle+=1
            fMach3.write(f'{lastSimulatedAngle}\t{ts}\n')
            time.sleep(SIMULATION_SLEEP)

        image = ch.takePicture()
        ts = time.time()

        listPic.append(image)
        listTime.append(ts)
        time.sleep(time_bt_pics)
    # endregion

    # region Saves all pictures and timestamp file
    with open('./TimedPictures/timeRelation.txt', 'w', encoding='UTF-8', errors='ignore') as f:
        for i, image in enumerate(listPic):
            cv2.imwrite(f'./TimedPictures/{i}_{listTime[i]}.jpg', image,)
            f.write(f'./TimedPictures/{i}.jpg\t{listTime[i]}\n')
    # endregion

    return listTime, listPic

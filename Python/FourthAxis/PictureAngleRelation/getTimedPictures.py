"""This file defines the getTimedPictures function, which is responsible for taking many pictures and storing the
relation between the time and the respective picture in order to prepare a sequence of pictures."""

import os, shutil
from CameraHandler.CameraHandler import *
from Mach3.Mach3Communication import *
import time
import random

# region Defined Constants

IS_SIMULATING_MACH3 = False
SIMULATION_SLEEP = 0.050
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60

DEFAULT_N_OF_SAMPLE = 400
DEFAULT_FOLDER_OF_PICTURES = './TimedPictures'
DEFAULT_TIME_BETWEEN_PICS_S = 0.2

MACH3_ANGLES_FILE = './TimedAngles/angle.txt'
random.seed()

# endregion

def getSecondsOfTheDay() -> float:
    """Returns number of seconds since the beginning of the day."""

    # Gets time in seconds since Epoch
    t = time.time()
    t_fraction = t - int(t)

    # Gets time struct
    localTime = time.localtime(t)

    # Converts to h:m:s informations
    h, m, s = localTime.tm_hour, localTime.tm_min, localTime.tm_sec

    # Converts to seconds since the beginning of the day
    daySeconds = h * SECONDS_PER_HOUR + m * SECONDS_PER_MINUTE + s + t_fraction

    return daySeconds

def convertSecOfDayToHMS(s: int) -> str:
    """Returns the string h:m:s using the input, which is the number of the seconds elapsed since the beginning of the day."""

    h = 0
    m = 0
    s = int(s)

    # Gets hours
    if (s / SECONDS_PER_HOUR) >= 0:
        h = int(s / SECONDS_PER_HOUR)
        s -= h * SECONDS_PER_HOUR

    # Gets minutes
    if (s / SECONDS_PER_MINUTE) >= 0:
        m = int(s / SECONDS_PER_MINUTE)
        s -= m * SECONDS_PER_MINUTE

    # The seconds are the remaining
    return f'{h}:{m}:{s}'

def getTimedPictures(n_of_samples=DEFAULT_N_OF_SAMPLE,
                     time_bt_pics=DEFAULT_TIME_BETWEEN_PICS_S,
                     folder_of_pic=None) -> tuple:

    # Prepares Camera. It's possible to change here for a specific camera instead of using a generic CameraHandler.
    ch = CameraHandler(startup_cam=True)

    mc = Mach3Communication(fromMach3File=r"C:\Windows\Temp\fromMach3.txt",
                            toMach3File=r"C:\Windows\Temp\toMach3.txt")
    mc.clearFromMach3()

    # region Prepares Mach3 simulation
    fMach3 = None
    if IS_SIMULATING_MACH3:
        fMach3 = open(MACH3_ANGLES_FILE, mode='w', encoding='UTF-8', errors='ignore')
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

    # region Takes pictures and keeps timestamp in number of seconds since the start of the day
    listPic = []
    listTime = []
    lastSimulatedAngle = 0

    print("Waiting for mach3...")
    mc.waitForString(str="go")
    print("Got GO signal, starting loop...")
    count = 0

    while (not mc.hasString(str='done')) and (count < n_of_samples):
        count += 1

        if IS_SIMULATING_MACH3:
            for i in range(int(random.random()*4)):
                ts = getSecondsOfTheDay()
                lastSimulatedAngle+=1
                fMach3.write(f'{lastSimulatedAngle}\t{ts}\n')
            time.sleep(SIMULATION_SLEEP)

        image = ch.takePicture()
        ts = getSecondsOfTheDay()

        listPic.append(image)
        listTime.append(ts)
        time.sleep(time_bt_pics)
    # endregion

    # region Saves all pictures and timestamp file
    print('\tSaving timed pictures...')
    with open('./TimedPictures/timeRelation.txt', 'w', encoding='UTF-8', errors='ignore') as f:
        for i, image in enumerate(listPic):
            cv2.imwrite(f'./TimedPictures/{i}_{listTime[i]}.jpg', image,)
            f.write(f'./TimedPictures/{i}.jpg\t{listTime[i]}\n')
    # endregion

    return listTime, listPic

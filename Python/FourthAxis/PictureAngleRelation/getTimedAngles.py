"""This file defines the getTimedAngles function, which is responsible for reading timestamp and respective angle from
a file written by Mach3 VBS implementation."""

def getTimedAngles() -> tuple:

    listAngle = []
    listTime = []

    with open('./TimedAngles/angle.txt', encoding='UTF-8', errors='ignore') as f:

        data = f.readlines()
        print('getTimedAngles:' + str(data))

        # region Separate angle and time from each line of the read file
        for line in data:

            line = line.replace('\n', '')
            angle, ts = line.split('\t', maxsplit=2)
            listAngle.append(float(angle))
            listTime.append(float(ts))
        # endregion

    return listTime, listAngle

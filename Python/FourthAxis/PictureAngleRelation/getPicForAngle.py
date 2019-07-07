"""This file defines the getPicsForAngles function, which is responsible for finding the relation between pictures
and angles using timestamp."""

from FourthAxis.PictureAngleRelation.getTimedPictures import *
from FourthAxis.PictureAngleRelation.getTimedAngles import *

import cv2

OUTPUT_FOLDER = './OutputForAlgo/'
TIMED_ANGLES_FILE = './TimedAngles/angle.txt'

def getPicsForAngles():

    # Get pictures and angles with timestamp

    print('Taking pictures...')
    tsPic, images = getTimedPictures()
    print(f'Loading angle file from {TIMED_ANGLES_FILE}...')
    tsAng, angles = getTimedAngles(timed_angles_file=TIMED_ANGLES_FILE)

    # region Check for errors
    print('Checking for errors in pictures and angles files...')

    if len(tsPic) != len(images):
        raise IOError('Length of tsPic is different than length of images.')
    if len(tsAng) != len(angles):
        raise IOError('Length of tsAng is different than length of angles.')
    # endregion

    # region Matches picture samples and angles
    print('Matching pictures and angles...')
    listMatch = []
    for iAngle, _ in enumerate(tsAng):

        tsCurrentAngle = tsAng[iAngle]

        for iPic, _ in enumerate(tsPic):

            if tsPic[iPic] < tsCurrentAngle:  # Case pic happened before the pose (useless)
                continue
            elif tsPic[iPic] >= tsCurrentAngle:  # Case pic happened after the pose (needs to still be on the pose)

                listMatch.append({'iAngle':iAngle, 'iPic':iPic})
                break
    # endregion

    # region Clean OutputForAlgo folder to avoid filling the HD in the future
    # Source of this part of the code:
    # https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder-in-python

    print('Cleaning output folder...')
    for the_file in os.listdir(OUTPUT_FOLDER):
        file_path = os.path.join(OUTPUT_FOLDER, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    # endregion

    # region Stores Output Files
    print('Saving output pictures...')
    with open(f'{OUTPUT_FOLDER}outputRelation.txt', mode='w', encoding='UTF-8', errors='ignore') as fOut:
        fOut.write('iAngle\tiPic\tts Ang\t\t\tAngle\tts Pic\n')
        for match in listMatch:

            outLine = str(match['iAngle']) + '\t' + str(match['iPic']) + '\t' + str(tsAng[match['iAngle']]) + '\t' + \
                      str(angles[match['iAngle']]) + '\t' + str(tsPic[match['iPic']]) + '\n'
            fOut.write(outLine)

            cv2.imwrite(f'{OUTPUT_FOLDER}pic{angles[match["iAngle"]]}.png', images[match['iPic']])
    print(f'\nDONE! Matching pictures saved in {OUTPUT_FOLDER}outputRelation.txt.')
    # endregion

getPicsForAngles()
"""This file contains the Mach3Communication class, responsible for managing the communication with Mach 3 in order
to send G codes and wait for its execution. Also, time constants are defined to protect the system from communication
errors.

Example of use in the Python Console:

from Mach3.Mach3Communication import *

gc = GCodeGenerator(5)

gc.getInitialCode()
gc.moveLinear(Point(0.5, 2, 3.7))

comm = Mach3Communication()
comm.runGCodeSafely(gc)

"""

import time
from GCodeGenerator.GCodeGenerator import *
import os

COMMUNICATION_TIMEOUT = 15  # Seconds
TIME_TO_WAIT_BEFORE_LINES = 0.3  # Seconds


class Mach3Communication(object):

    def __init__(self, fromMach3File: str = 'fromMach3.txt', toMach3File: str = 'toMach3.txt',
                 print_comms=False):
        """
        Responsible for managing the communication with Mach 3 in order to send G codes and wait for its execution.
        :param fromMach3File: file with Mach3 response.
        :param toMach3File: file with messages to be send to Mach3.
        """

        # Gets names/paths of communication files
        self.fromMach3File = fromMach3File
        self.toMach3File = toMach3File

        self.print_comms = print_comms

        # Cleans file to Mach3 just in case there is garbage in the folder
        self.clearOK()

    def hasString(self, str="ok"):
        with open(self.fromMach3File, 'r') as fFromMach3:
            text = fFromMach3.readline()
            if self.print_comms:
                print('Read from Mach3: ' + text)

        if text == str+'\n':
            return True
        else:
            return False

    def waitForString(self, str="ok", timeout=True):
        """
        Waits for Mach3 response till it turns 'string'. Timeout defined in COMMUNICATION_TIMEOUT constant, if not
        respected a TimeoutError exception will be raised.
        """

        receivedOk = False

        t0 = time.time()
        while not receivedOk:

            with open(self.fromMach3File, 'r') as fFromMach3:
                text = fFromMach3.readline()
                if self.print_comms:
                    print('Read from Mach3: ' + text)
                time.sleep(TIME_TO_WAIT_BEFORE_LINES)

            if text == str+'\n':
                receivedOk = True

            if timeout and ((time.time() - t0) > COMMUNICATION_TIMEOUT):

                # TODO: ADD LOGIC TO PROTECT CNC FROM MACH3. I.E. TURN MOTORS OFF ELECTRICALLY?

                raise(TimeoutError("Communication with Mach3 is taking too long."))

    def waitForOK(self):
        """
        Waits for Mach3 response till it turns 'ok'. Timeout defined in COMMUNICATION_TIMEOUT constant, if not
        respected a TimeoutError exception will be raised.
        """

        receivedOk = False

        t0 = time.time()
        while not receivedOk:

            with open(self.fromMach3File, 'r') as fFromMach3:
                text = fFromMach3.readline()
                if self.print_comms:
                    print('Read from Mach3: ' + text)
                time.sleep(TIME_TO_WAIT_BEFORE_LINES)

            if text == 'ok\n':
                receivedOk = True

            if (time.time() - t0) > COMMUNICATION_TIMEOUT:

                # TODO: ADD LOGIC TO PROTECT CNC FROM MACH3. I.E. TURN MOTORS OFF ELECTRICALLY?

                raise(TimeoutError("Communication with Mach3 is taking too long."))

    def sendOK(self):
        """Informs Mach3 Python has completed its job. Now its time for Mach3 to run the G Code."""

        with open(self.toMach3File, 'w') as fToMach3:
            fToMach3.write('ok')

    def clearOK(self):
        """
        Removes Python OK, so Mach3 won't present communication issues.
        """

        open(self.toMach3File, 'w').close()

    def clearFromMach3(self) -> int:
        """
        If possible, cleans file with Mach3 outputs (python inputs) to prevent Python from communication issues.
        :return: 0 if Python managed to clean the file, 1 otherwise.
        """

        nok = 0

        if os.access(self.fromMach3File, os.W_OK):
            open(self.fromMach3File, 'w').close()
        else:
            nok = 1

        return nok

    def waitForMach3(self):
        """
        Full process of sending OK to Mach3, waiting for answer and cleaning toMach3 communication file.
        """

        self.sendOK()
        self.waitForOK()
        self.clearOK()

    def runGCodeSafely(self, gc: GCodeGenerator):
        """
        Runs safely G Code outputted by GCodeGenerator after adding a new line at the end of the file.
        Here, to run safely means the full process of cleaning communication files, sending OK to Mach3,
        waiting for answer and cleaning toMach3 communication file.
        :param gc: GCodeGenerator object so this method can add empty line at the end of the generated G Code.
        """
        self.clearOK()
        if os.access(self.fromMach3File, os.R_OK):
            self.clearFromMach3()

        # This is necessary because Mach3 doesn't read the last code line
        gc.insertNewLine()

        # Sends OK to Mach3, waits for its confirmation that it's free again then cleans Python OK
        self.waitForMach3()

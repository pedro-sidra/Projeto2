"""This file defines the Point and GCodeGenerator classes. The first is responsible for storing 3D positions and the
second is used to generate G Code."""

from enum import IntEnum
from proj2.GCodeGenerator.GCodeChooser import *
from tkinter import Tk


class OutputMethod(IntEnum):
    """Enumeration for output: STRING only or FILE (default)."""
    STRING = 0
    FILE = 1


class SpindleStatus(IntEnum):
    """Enumeration for Spindle status."""
    CW = 0
    CCW = 1
    OFF = 2


class Point(object):

    def __init__(self, x: float, y: float, z: float):

        self.__x = 0.0
        self.__y = 0.0
        self.__z = 0.0

        self.setPoint(x, y, z)

    def setPoint(self, x: float, y: float, z: float):
        """Configs the points based on inputs x, y and z."""

        self.__x = float(x)
        self.__y = float(y)
        self.__z = float(z)

    def getPoint(self) -> []:
        """Returns a list of the three coordinates."""

        return [self.__x, self.__y, self.__z]


class GCodeGenerator(object):

    def __init__(self, tool_diameter: int, feed_rate: int = 1000, speed: int = 2000, angle_to_align: float = 0.0,
                 output_method: OutputMethod = OutputMethod.FILE, output_file='out.tap'):
        """
        GCodeGenerator class is responsible for GCodeGeneration.
        :param tool_diameter: The tool diameter used for radius corrections.
        :param feed_rate: Feed Rate used for G1.
        :param speed: Spingle rotation speed.
        :param angle_to_align: Angle to rotate.
        :param output_method: OutputMethod(IntEnum).
        :param output_file: name/path of the generated code file.
        """
        # Operation
        self.feed_rate = feed_rate
        self.speed = speed
        self.tool_diameter = tool_diameter
        self.angle_to_align = angle_to_align

        # Output
        self.output_file = output_file
        self.output_method = output_method
        self.current_line = 1

        # Prepares file
        self.cleanFile()

    # region Private methods

    def __convertNewLines(self, code: str):

        # Replaces every line with line number
        next_new_line = code.find('\n')
        while next_new_line > -1:

            # Prepares and replaces '\n' string for line number
            line_number = str(self.current_line)
            while len(line_number) < 3:
                line_number = '0' + line_number
            line_number = '{NL}N' + line_number + ' '
            code = code.replace('\n', line_number, 1)

            # Goes for next occurrence
            next_new_line = code.find('\n')
            self.current_line += 1

        code = code.replace('{NL}', '\n')
        return code

    def __outputCode(self, code: str):

        if self.output_method == OutputMethod.FILE:
            with open(self.output_file, 'a') as f:
                f.write(code)
        return code

    # endregion

    def cleanFile(self):
        """Cleans output file."""

        with open(self.output_file, 'w') as f:
            f.write('; Generated Code:')

    def insertNewLine(self):
        """Adds new numbered line."""

        self.writeManualCodeToFile("\n")

    def resetReference(self):
        """Puts the reference on the home position."""

        self.__outputCode("G92.1")

    def setReference(self, point: Point):
        """Sets the reference."""

        x, y, z = point.getPoint()

        code = '{NL}; Setting the reference'
        code += '\nG92 X%s Y%s Z%s' % (x, y, z)

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def rotateCoordinateSystem(self, angle):
        code = '{NL}; Rotating the coordinate system'
        code += '\nG68 A0 B0 R%s' % (angle)

        code = self.__convertNewLines(code)
        return self.__outputCode(code)


    def enterRelativeMode(self):
        """Changes to relative position mode."""

        self.writeManualCodeToFile("G91")

    def enterAbsoluteMode(self):
        """Changes to absolute position mode."""

        self.writeManualCodeToFile("G90")

    def getInitialCode(self):
        """Returns CNC initial ocnfigurations."""

        # TODO: prepare the initial commands to configure the machine
        code = '{NL}; Initial code to prepare machine and environment'
        code += '\nG90'  # Absolute
        code += '\nG21'  # Millimeters
        code += '\nG94'  # Units per Minute

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def moveFast(self, point: Point):
        """Runs fast movement. The path may not be linear."""

        x, y, z = point.getPoint()

        code = '{NL}; Moving as fast as possible'
        code += '\nG0 X%s Y%s Z%s' % (x, y, z)

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def moveLinear(self, point: Point, feed_rate: int = None):
        """Moves linearly to the 'point' position by moving in 'feed_Rate' speed."""


        x, y, z = point.getPoint()
        feed_rate = self.feed_rate if feed_rate is None else feed_rate

        code = '{NL}; Moving Linearly'
        code += '\nG0 F%s' % feed_rate
        code += '\nG0 X%s Y%s Z%s' % (x, y, z)

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def setSpindle(self, spindle_status: SpindleStatus, speed: int = None):
        """Sets spindle rotation.
        :param spindle_status: SpindleStatus(IntEnum).
        :param speed: rotational speed.
        :return: generated code for spindle configuration.
        """

        speed = self.speed if speed is None else speed

        code = ''
        if spindle_status == SpindleStatus.CW:
            code += '{NL}; Turning Spindle CW'
            code += '\nM3 S%s' % speed
        elif spindle_status == SpindleStatus.CCW:
            code += '{NL}; Turning Spindle CCW'
            code += '\nM4 S%s' % speed
        else:
            code += '{NL}; Stopping Spindle rotation'
            code += '\nM5'

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def writeManualCodeToFile(self, manual_code: str, include_new_line = True):
        """Adds 'manual_code' to the file. A new numbered line is added to the beginning if 'include_new_line'
        parameter is True."""

        if include_new_line:
            manual_code = '\n' + manual_code

        manual_code = self.__convertNewLines(manual_code)
        return self.__outputCode(manual_code)

    def runAlignedToPlaneCommand(self, subprogram: int, angle: float = None):
        """Runs subprogram number 'subprogram' rotated by 'angle'."""

        angle = self.angle_to_align if angle is None else angle
        angle = str(angle)

        code = '{NL}; Running subprogram %s rotated by %s degrees' % (subprogram, angle)
        code += '\nG68 X0 Y0 R%s M98 P%s' % (angle, subprogram)
        code += '\nG69'

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def startSubprogramDefinition(self, id: int):
        """Starts definition of subprogram number 'id'."""

        code = '{NL}{NL}; Subprogram %s definition' % id
        code += '\nO%s' % id

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def finishSubprogramDefinition(self):
        """Finishes subprogram definition."""

        code = '{NL}; Finishing subprogram definition'
        code += '\nM99'
        code += '{NL}'

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def loadGCode(self, path=None) -> bool:
        """Loads G Code from a file and appends to output file.
        :param path: If None, a dialog will open to find file. Otherwise, will use 'path' as the file path.
        :return: True if importing was successful, False otherwise.
        """

        ret = False
        # region Gets file path from parameter or GUI. Path is 'None' if file is not selected.
        if path is None:

            master = Tk()
            gui = GCodeChooser(master)
            master.mainloop()

            # 'gcode_user_file_path' is a variable from GCodeChooser class
            try:
                path = gui.getFilePath()
            except:
                path = None

        else:
            path = path

        # endregion

        if path is not None:

            try:
                with open(path, mode='r') as f:

                    lines = f.readlines()
                    gc.writeManualCodeToFile('{NL}{NL}; START OF IMPORTED CODE{NL}', include_new_line = False)

                    for line in lines:
                        line = line.replace('\n', '')
                        self.writeManualCodeToFile(line)

                    gc.writeManualCodeToFile('{NL}{NL}; END OF IMPORTED CODE{NL}', include_new_line=False)
                    ret = True
            except:
                print('Issue while trying to load file.')

        else:
            print('File not selected, therefore not used.')

        return ret


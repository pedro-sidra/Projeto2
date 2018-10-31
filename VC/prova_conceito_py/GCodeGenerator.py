from enum import IntEnum


class OutputMethod(IntEnum):
    STRING = 0
    FILE = 1


class SpindleStatus(IntEnum):
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

        self.__x = float(x)
        self.__y = float(y)
        self.__z = float(z)

    def getPoint(self) -> []:

        return [self.__x, self.__y, self.__z]


class GCodeGenerator(object):

    def __init__(self, tool_diameter: int, feed_rate: int = 1000, speed: int = 2000, angle_to_align: float = 0.0,
                 output_method: OutputMethod = OutputMethod.FILE, output_file='out.tap'):

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

        with open(self.output_file, 'w') as f:
            f.write('; Generated Code:')

    def insertNewLine(self):
        self.__outputCode("\n")

    def enterRelativeMode(self):
        self.writeManualCodeToFile("G91")

    def enterAbsoluteMode(self):
        self.writeManualCodeToFile("G90")

    def getInitialCode(self):

        # TODO: prepare the initial commands to configure the machine
        code = '{NL}; Initial code to prepare machine and environment'
        code += '\nG90'  # Absolute
        code += '\nG21'  # Millimeters
        code += '\nG94'  # Units per Minute

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def moveFast(self, point: Point):

        x, y, z = point.getPoint()

        code = '{NL}; Moving as fast as possible'
        code += '\nG0 X%s Y%s Z%s' % (x, y, z)

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def moveLinear(self, point: Point, feed_rate: int = None):
        x, y, z = point.getPoint()
        feed_rate = self.feed_rate if feed_rate is None else feed_rate

        code = '{NL}; Moving Linearly'
        code += '\nG1 F%s' % feed_rate
        code += '\nG1 X%s Y%s Z%s' % (x, y, z)

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def setSpindle(self, spindle_status: SpindleStatus, speed: int = None):

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

    def writeManualCodeToFile(self, manual_code: str):

        manual_code = '\n' + manual_code
        manual_code = self.__convertNewLines(manual_code)
        return self.__outputCode(manual_code)

    def runAlignedToPlaneCommand(self, subprogram: int, angle: float = None):

        angle = self.angle_to_align if angle is None else angle
        angle = str(angle)

        code = '{NL}; Running subprogram %s rotated by %s degrees' % (subprogram, angle)
        code += '\nG68 X0 Y0 R%s M98 P%s' % (angle, subprogram)
        code += '\nG69'

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def startSubprogramDefinition(self, id: int):

        code = '{NL}{NL}; Subprogram %s definition' % id
        code += '\nO%s' % id

        code = self.__convertNewLines(code)
        return self.__outputCode(code)

    def finishSubprogramDefinition(self):

        code = '{NL}; Finishing subprogram definition'
        code += '\nM99'
        code += '{NL}'

        code = self.__convertNewLines(code)
        return self.__outputCode(code)


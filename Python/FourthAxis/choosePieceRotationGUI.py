"""This file defines the PieceRotationGUI class and the getChosenPieceRotation function. To use the GUI, just call the
function and read its returned value.

If the return is a number, that's the angle that the figure must be rotated. If it's None, the user has cancelled.

"""

from tkinter import *
from PIL import Image, ImageTk
from Mach3.Mach3Communication import *

GRID_LINE_STEP = 10


class PieceRotationGUI:

    def __init__(self, master, piece_img_file="hex.gif", img_size=256, canvas_size=None):

        # region Mach3 communication
        self.gc = GCodeGenerator(0, output_file=r"C:\Windows\Temp\out.tap")
        self.mc = Mach3Communication(fromMach3File=r"C:\Windows\Temp\fromMach3.txt",
                                toMach3File=r"C:\Windows\Temp\toMach3.txt")
        self.gc.cleanFile()
        self.mc.clearFromMach3()
        self.mc.clearOK()
        # endregion

        self.current_angle = 0
        self.master = master
        master.title("Orientação da Peça")

        # region Configuration

        self.label = Label(master, text="Rotacione a peça como desejado e pressione 'OK' para finalizar setup.")
        self.label.pack()

        if canvas_size is None:
            canvas_size = img_size

        self.canvas = Canvas(self.master, width=canvas_size, height=canvas_size)
        self.canvas.pack(expand=False)

        self.loadedPilImage = Image.open(piece_img_file)
        self.pilImage = self.loadedPilImage.rotate(0)
        self.img = ImageTk.PhotoImage(self.pilImage)

        self.imgOnCanvas = self.canvas.create_image(img_size / 2, img_size / 2, anchor=CENTER, image=self.img)
        self.canvas.after(50, self.__updateImageCanvas)
        self.canvas.bind('<Configure>', self.__create_grid)

        self.rotPlus_button = Button(master, text="+", command=self.bnPlus)
        self.rotPlus_button.pack()

        self.rotMinus_button = Button(master, text="-", command=self.bnMinus)
        self.rotMinus_button.pack()

        self.newAngle_entry = Entry(master)
        self.newAngle_entry.pack()

        self.apply_button = Button(master, text="Apply Written Angle to Image", command=self.bnApply)
        self.apply_button.pack()

        self.labelCurrentAngle = Label(master, text=f"Current angle: {self.current_angle} deg.")
        self.label.after(50, self.__updateCurrentAngleLabel)
        self.labelCurrentAngle.pack()

        self.rotate_piece = Button(master, text="Rotate piece using Mach3", command=self.bnRotate)
        self.rotate_piece.pack()

        self.greet_button = Button(master, text="OK", command=self.bnOk)
        self.greet_button.pack()

        self.close_button = Button(master, text="Cancel", command=self.bnCancel)
        self.close_button.pack()

        # endregion

    def bnPlus(self):

        self.current_angle += 1

    def bnMinus(self):

        self.current_angle -= 1

    def bnApply(self):

        value = self.newAngle_entry.get()
        try:
            value = float(value)
        except:
            value = 0

        self.current_angle = value

    def bnRotate(self):

        self.mc.clearFromMach3()

        # Clear the G Code file and prepare the code
        self.gc.cleanFile()
        self.gc.getInitialCode()
        self.gc.writeManualCodeToFile(f'G0 A{self.current_angle}')
        self.gc.insertNewLine()

        # Starts to run G code, waits for it to execute and clears files
        self.mc.waitForMach3()
        self.mc.clearFromMach3()
        self.gc.cleanFile()

    def bnOk(self):

        self.__finishLoopMach3()
        time.sleep(0.5)
        self.master.destroy()

    def bnCancel(self):

        self.__finishLoopMach3()
        self.current_angle = None
        time.sleep(0.5)
        self.master.quit()

    def getCurrentAngle(self):

        return self.current_angle

    def __updateCurrentAngleLabel(self):

        self.labelCurrentAngle.configure(text=f"Current angle: {self.current_angle} deg.")
        self.label.after(50, self.__updateCurrentAngleLabel)

    def __updateImageCanvas(self):

        self.pilImage = self.loadedPilImage.rotate(self.current_angle)
        self.img = ImageTk.PhotoImage(self.pilImage)
        self.canvas.itemconfig(self.imgOnCanvas, image=self.img)
        self.canvas.after(50, self.__updateImageCanvas)

    def __finishLoopMach3(self):

        with open(self.mc.toMach3File, 'w') as fToMach3:
            fToMach3.write('exit')

        self.mc.clearFromMach3()
        self.gc.cleanFile()

    def __create_grid(self, event=None):
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        self.canvas.delete('grid_line')  # Will only remove the grid_line

        # Creates all vertical lines at intevals of GRID_LINE_STEP
        for i in range(0, w, GRID_LINE_STEP):
            self.canvas.create_line([(i, 0), (i, h)], tag='grid_line', fill='gray')

        # Creates all horizontal lines at intevals of GRID_LINE_STEP
        for i in range(0, h, GRID_LINE_STEP):
            self.canvas.create_line([(0, i), (w, i)], tag='grid_line', fill='gray')


def getChosenPieceRotation(piece_img_file="hex.gif"):
    master = Tk()
    gui = PieceRotationGUI(master, piece_img_file=piece_img_file)
    master.mainloop()

    print(gui.current_angle)

    return gui.current_angle


getChosenPieceRotation(piece_img_file="hex.gif")

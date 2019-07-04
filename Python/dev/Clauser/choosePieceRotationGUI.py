"""This file defines the PieceRotationGUI class and the getChosenPieceRotation function. To use the GUI, just call the
function and read its returned value.

If the return is a number, that's the angle that the figure must be rotated. If it's None, the user has cancelled.

"""

from tkinter import *
from PIL import Image, ImageTk


class PieceRotationGUI:

    def __init__(self, master, piece_img_file="hex.gif", img_size=255):

        self.current_angle = 0

        self.master = master
        master.title("Orientação da Peça")

        # region Configuration

        self.label = Label(master, text="Rotacione a peça como desejado e pressione 'OK' para finalizar setup.")
        self.label.pack()

        self.canvas = Canvas(self.master, width=img_size, height=img_size)
        self.canvas.pack()

        self.loadedPilImage = Image.open(piece_img_file)
        self.pilImage = self.loadedPilImage.rotate(0)
        self.img = ImageTk.PhotoImage(self.pilImage)

        self.imgOnCanvas = self.canvas.create_image(img_size / 2, img_size / 2, anchor=CENTER, image=self.img)
        self.canvas.after(50, self.__updateImageCanvas)

        self.rotPlus_button = Button(master, text="+", command=self.bnPlus)
        self.rotPlus_button.pack()

        self.rotMinus_button = Button(master, text="-", command=self.bnMinus)
        self.rotMinus_button.pack()

        self.newAngle_entry = Entry(master)
        self.newAngle_entry.pack()

        self.apply_button = Button(master, text="Apply Angle", command=self.bnApply)
        self.apply_button.pack()

        self.labelCurrentAngle = Label(master, text=f"Current angle: {self.current_angle} deg.")
        self.label.after(50, self.__updateCurrentAngleLabel)
        self.labelCurrentAngle.pack()

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

    def bnOk(self):

        self.master.destroy()

    def bnCancel(self):

        self.current_angle = None
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


def getChosenPieceRotation(piece_img_file="hex.gif"):
    master = Tk()
    gui = PieceRotationGUI(master, piece_img_file=piece_img_file)
    master.mainloop()

    print(gui.current_angle)

    return gui.current_angle


getChosenPieceRotation(piece_img_file="hex.gif")

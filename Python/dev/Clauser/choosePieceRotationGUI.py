
from tkinter import *

piece_angle = 0  # deg

class GCodeChooser:

    def __init__(self, master, piece_img_file="hex.gif", img_size=255):

        self.master = master
        master.title("Orientação da Peça")

        self.label = Label(master, text="Rotacione a peça como desejado e pressione 'OK' para finalizar setup.")
        self.label.pack()

        canvas = Canvas(self.master, width=img_size, height=img_size)
        canvas.pack()
        self.img = PhotoImage(file=piece_img_file)
        canvas.create_image(img_size/2, img_size/2, anchor=CENTER, image=self.img)

        self.rotPlus_button = Button(master, text="+", command=self.bnPlus)
        self.rotPlus_button.pack()

        self.rotMinus_button = Button(master, text="-", command=self.bnMinus)
        self.rotMinus_button.pack()

        self.greet_button = Button(master, text="OK", command=self.bnOk)
        self.greet_button.pack()

        self.close_button = Button(master, text="Cancel", command=master.quit)
        self.close_button.pack()

    def bnPlus(self):

        global piece_angle
        piece_angle += 1

    def bnMinus(self):

        global piece_angle
        piece_angle -= 1

    def bnOk(self):

        self.master.destroy()


master = Tk()
my_gui = GCodeChooser(master)
master.mainloop()

print(piece_angle)

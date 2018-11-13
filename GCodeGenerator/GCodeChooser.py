"""This file defines the GCodeChooser class, which is responsible for allowing the user to select the file to be
loaded."""

from tkinter import Tk, Label, Button
from tkinter import filedialog

gcode_user_file_path = None

class GCodeChooser:

    def __init__(self, master):
        """Implements a simple GUI to ask for file selection."""

        self.master = master
        master.title("Choose the G Code...")

        self.label = Label(master, text="Press to choose file whenever you are ready!")
        self.label.pack()

        self.choose_button = Button(master, text="Choose File", command=self.chooseFile)
        self.choose_button.pack()

        self.cancel_button = Button(master, text="Cancel", command=master.quit)
        self.cancel_button.pack()


    def chooseFile(self):
        """When the choose_button is pressed, a dialog is opened to choose the file that contains G Code."""

        global gcode_user_file_path
        options = {}

        options['title'] = 'Loading G Code for piece...'
        options['initialdir'] = 'C:\\'
        gcode_user_file_path = filedialog.askopenfilename(**options)

        self.master.destroy()

    def getFilePath(self):
        """Returns the chosen file path, if already chosen. Raises exception otherwise."""

        if gcode_user_file_path is not None:
            return gcode_user_file_path
        else:
            raise(FileNotFoundError('File not chosen.'))

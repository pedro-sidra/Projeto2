
from tkinter import Tk, Label, Button
from tkinter import filedialog

gcode_user_file_path = None

class GCodeChooser:

    def __init__(self, master):

        self.master = master
        master.title("Choose the G Code...")

        self.label = Label(master, text="Press to choose file whenever you are ready!")
        self.label.pack()

        self.greet_button = Button(master, text="Choose File", command=self.chooseFile)
        self.greet_button.pack()

        self.close_button = Button(master, text="Cancel", command=master.quit)
        self.close_button.pack()

    def chooseFile(self):

        global gcode_user_file_path
        options = {}

        options['title'] = 'Loading G Code for piece...'
        options['initialdir'] = 'C:\\'
        file_path = filedialog.askopenfilename(**options)

        self.master.destroy()


# master = Tk()
# my_gui = GCodeChooser(master)
# master.mainloop()
#
# print(file_path)

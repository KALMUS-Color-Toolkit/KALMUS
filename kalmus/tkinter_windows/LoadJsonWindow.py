""" LoadJsonWindow Class """

import tkinter.filedialog
from tkinter.messagebox import showerror, showinfo
import copy
import os

from kalmus.tkinter_windows.gui_utils import resource_path, update_graph


class LoadJsonWindow():
    """
    loadJsonWindow Class
    GUI window for user to load the barcode from existed json file to replace with the barcode in the main window
    """
    def __init__(self, barcode_generator, barcode_1, barcode_2, axes,
                 canvas, barcode_stack):
        """
        Initialize

        :param barcode_generator: The barcode generator
        :param barcode_1: The barcode 1
        :param barcode_2: The barcode 2
        :param axes: The axes of the plotted figure in the main window
        :param canvas: The canvas of the plotted figure in the main window
        :param barcode_stack: The dictionary that stores all the barcode on memory
        """
        self.barcode_generator = barcode_generator
        self.barcode_1 = barcode_1
        self.barcode_2 = barcode_2

        # Set up the axes and canvas
        self.axes = axes
        self.canvas = canvas

        self.barcode_stack = barcode_stack

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Load JSON Barcode")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Label prompt for the file name/path to the json file
        filename_label = tkinter.Label(self.window, text="JSON file path: ")
        filename_label.grid(row=0, column=0, sticky=tkinter.W)

        # Text entry for user to type the file name/path to the json file
        self.filename_entry = tkinter.Entry(self.window, textvariable="", width=40)
        self.filename_entry.grid(row=0, column=1, columnspan=2, sticky=tkinter.W)

        # Label prompt for user to specify the type of the barcode they will load
        barcode_type_label = tkinter.Label(self.window, text="Specify Barcode Type: ")
        barcode_type_label.grid(row=1, column=0, sticky=tkinter.W)

        # The variable that stores the type of barcode
        self.type_variable = tkinter.StringVar(self.window)
        self.type_variable.set("Color")

        # The dropdown menu for user to select the type of the loaded barcode
        dropdown_type = tkinter.OptionMenu(self.window, self.type_variable, "Color", "Brightness")
        dropdown_type.grid(row=1, column=1, sticky=tkinter.W)

        # Button to build/load the barcode using the given json file
        self.button_build_barcode = tkinter.Button(self.window, text="Load", command=self.build_barcode)
        self.button_build_barcode.grid(row=2, column=3, columnspan=1)

        # Button to browse the folder
        self.button_browse_folder = tkinter.Button(self.window, text="Browse", command=self.browse_folder)
        self.button_browse_folder.grid(row=0, column=3)

        # Variable that stores whcih barcode in the main window to replace with
        self.barcode_option = tkinter.StringVar(self.window)
        self.barcode_option.set("Barcode 1")

        # Radio button for selecting which barcode in the main window to replace with
        radio_barcode_1 = tkinter.Radiobutton(self.window, text="Barcode 1", variable=self.barcode_option,
                                            value="Barcode 1", anchor='w')
        radio_barcode_1.grid(row=1, column=2, sticky=tkinter.W)
        radio_barcode_1.select()

        radio_barcode_2 = tkinter.Radiobutton(self.window, text="Barcode 2", variable=self.barcode_option,
                                           value="Barcode 2", anchor='w')
        radio_barcode_2.grid(row=2, column=2, sticky=tkinter.W)

    def browse_folder(self):
        """
        Browse the folder to locate the json file
        """
        # Get the file name from the user selection
        filename = tkinter.filedialog.askopenfilename(initialdir=".", title="Select JSON file",
                                                      filetypes=(("json files", "*.json"), ("txt files", "*.txt"),
                                                                 ("All files", "*.*")))

        # Update the file name to the file name text entry
        self.filename_entry.delete(0, tkinter.END)
        self.filename_entry.insert(0, filename)

    def build_barcode(self):
        """
        Build/load the barcode use the json file
        """
        # Get the file name/path to the json file
        filename = self.filename_entry.get()

        # Check if the filename is given
        if not os.path.exists(filename):
            showerror("JSON File Not Exists", "JSON file not exists.\n"
                                              "Please check the JSON file path.")
            return

        try:
            # Generate the barcode from json file use the barcode generator
            barcode_type = self.type_variable.get()
            self.barcode_generator.generate_barcode_from_json(filename, barcode_type)
        except:
            showerror("Error Occurred in Loading JSON Barcode", "An error occurred in loading the JSON barcode.\n\n"
                                                                "Please make sure the type of Barcode saved\n"
                                                                "in the JSON file is correctly specified.\n"
                                                                "Color or Brightness")
            return

        # Get the name of the json file
        start_pos = filename.rfind("/") + 1
        if start_pos < 0:
            start_pos = 0

        # Use that as the key to the newly built/loaded barcode
        barcode_name = filename[start_pos: filename.rfind(".json")]
        self.barcode_stack[barcode_name] = copy.deepcopy(self.barcode_generator.get_barcode())

        # Get which barcode in the main window to replace with
        which_barcode = self.barcode_option.get()
        if which_barcode == "Barcode 1":
            self.barcode_1.__dict__ = self.barcode_generator.get_barcode().__dict__.copy()
            self.barcode_1.__class__ = self.barcode_generator.get_barcode().__class__
        elif which_barcode == "Barcode 2":
            self.barcode_2.__dict__ = self.barcode_generator.get_barcode().__dict__.copy()
            self.barcode_2.__class__ = self.barcode_generator.get_barcode().__class__

        # Clear the plotted axes in the main window
        self.axes[0][0].cla()
        self.axes[1][0].cla()
        self.axes[0][1].cla()
        self.axes[1][1].cla()

        # Always plotted the barcode with longer width below
        if self.barcode_1.get_barcode().shape[1] > self.barcode_2.get_barcode().shape[1]:
            temp = copy.deepcopy(self.barcode_1)

            self.barcode_1.__dict__ = self.barcode_2.__dict__.copy()
            self.barcode_2.__dict__ = temp.__dict__.copy()

        # Update the graph/plotted figure in the main window
        update_graph(barcode_1=self.barcode_1, barcode_2=self.barcode_2, axes=self.axes)

        # Redraw the main window
        self.canvas.draw()

        # Quit the main window
        self.window.destroy()

        showinfo("Barcode Loaded Successfully", "{:s} Barcode has been successfully loaded into the memory.\n\n"
                                                "Name key in memory: {:20s}".format(barcode_type, barcode_name))

""" LoadStackWindow Class """

import tkinter
from kalmus.tkinter_windows.gui_utils import update_graph, resource_path
import copy


class LoadStackWindow():
    """
    LoadStackWindow Class
    GUI window for user to load the barcode from the memory into the main window of the kalmus
    """
    def __init__(self, barcode_stack, barcode_1, barcode_2, axes, canvas):
        """
        Initialize

        :param barcode_stack: The dictionary that stores all the barcode on memory
        :param barcode_1: The barcode 1
        :param barcode_2: The barcode 2
        :param axes: The plotted figure axes in the main window
        :param canvas: The plotted figure canvas in the main window
        """
        self.barcode_stack = barcode_stack
        self.barcode_1 = barcode_1
        self.axes = axes
        self.canvas = canvas
        self.barcode_2 = barcode_2

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))
        self.window.wm_title("Barcodes on Memory Stack")

        # Set up the list box that shows all the barcode on memory using their keys in the dictionary
        self.listbox = tkinter.Listbox(self.window, selectmode=tkinter.SINGLE, width=65, height=20)
        self.listbox.grid(row=0, column=0)

        # List all the barcodes with their keys
        for barcode_names in self.barcode_stack.keys():
            self.listbox.insert(tkinter.END, barcode_names)

        # Button to load the barcode from the memory
        self.button_load = tkinter.Button(master=self.window, text="Load Selected Barcode", command=self.load_stack)
        self.button_load.grid(row=3, column=0, sticky=tkinter.W)

        # Option variable that stores the position which the new barcode from json will replace with
        self.barcode_option = tkinter.StringVar(self.window)
        self.barcode_option.set("Barcode 1")

        # Radio buttons for the replaced barcode selection
        radio_barcode_1 = tkinter.Radiobutton(self.window, text="Barcode 1", variable=self.barcode_option,
                                              value="Barcode 1", anchor='w')
        radio_barcode_1.grid(row=1, column=0, sticky=tkinter.W)
        radio_barcode_1.select()

        radio_barcode_2 = tkinter.Radiobutton(self.window, text="Barcode 2", variable=self.barcode_option,
                                              value="Barcode 2", anchor='w')
        radio_barcode_2.grid(row=2, column=0, sticky=tkinter.W)

    def load_stack(self):
        """
        Load the barcode from the memory and use it to replace one of the displayed barcodes in the main window
        """
        # Get the selection of the barcode on memory
        barcode_key = str(self.listbox.get(self.listbox.curselection()))

        # Get which barcode in the main window to replace
        which_barcode = self.barcode_option.get()

        # Replace with the barcode in the main window
        if which_barcode == "Barcode 1":
            self.barcode_1.__dict__ = copy.deepcopy(self.barcode_stack[barcode_key].__dict__.copy())
            self.barcode_1.__class__ = self.barcode_stack[barcode_key].__class__
        elif which_barcode == "Barcode 2":
            self.barcode_2.__dict__ = copy.deepcopy(self.barcode_stack[barcode_key].__dict__.copy())
            self.barcode_2.__class__ = self.barcode_stack[barcode_key].__class__

        # Clear the axes
        self.axes[0][0].cla()
        self.axes[1][0].cla()
        self.axes[0][1].cla()
        self.axes[1][1].cla()

        # Always plot the barcode with longer width below
        if self.barcode_1.get_barcode().shape[1] > self.barcode_2.get_barcode().shape[1]:
            temp = copy.deepcopy(self.barcode_1)

            self.barcode_1.__dict__ = self.barcode_2.__dict__.copy()
            self.barcode_2.__dict__ = temp.__dict__.copy()

        # Update the graph/plotted figure in the main window
        update_graph(barcode_1=self.barcode_1, barcode_2=self.barcode_2, axes=self.axes)

        # Redraw the canvas
        self.canvas.draw()

        # Quit the window
        self.window.destroy()

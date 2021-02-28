""" WhichBarcodeInspectWindow Class """

import tkinter
from kalmus.tkinter_windows.plot_barcodes_windows.PlotBarcodeWindow import PlotBarcodeWindow
from kalmus.tkinter_windows.gui_utils import resource_path


class WhichBarcodeInspectWindow():
    """
    WhichBarcodeInspectWindow Class
    GUI window for user to select which barcode to inspect in detail
    """
    def __init__(self, barcode_1, barcode_2, figsize=(6, 4), dpi=100):
        """
        Initialize

        :param barcode_1: The barcode 1
        :param barcode_2: The barcode 2
        :param figsize: The size of the figure plotted in the window
        :param dpi: dpi of the plotted figure
        """
        self.barcode_1 = barcode_1
        self.barcode_2 = barcode_2
        self.figsize = figsize
        self.dpi = dpi

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Which Barcode to Inspect")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Barcode option variable
        self.barcode_option = tkinter.StringVar(self.window)
        self.barcode_option.set("Barcode 1")

        # Option radio button
        radio_barcode_1 = tkinter.Radiobutton(self.window, text="Barcode 1", variable=self.barcode_option,
                                              value="Barcode 1")
        radio_barcode_1.grid(row=0, column=0, padx=50)
        radio_barcode_1.select()

        radio_barcode_2 = tkinter.Radiobutton(self.window, text="Barcode 2", variable=self.barcode_option,
                                              value="Barcode 2")
        radio_barcode_2.grid(row=1, column=0, padx=50)

        # Inspect the barcode button
        self.button_inspect = tkinter.Button(master=self.window, text="Inspect", command=self.inspect_barcode)
        self.button_inspect.grid(row=2, column=0, padx=50)

    def inspect_barcode(self):
        """
        Inspect the selected barcode once user press inspect button
        """
        # Get the selection from the user
        which_barcode = self.barcode_option.get()

        # Quit the current window
        self.window.destroy()

        # Instantiate the PlotBarcodeWindow using the user selection
        if which_barcode == "Barcode 1":
            PlotBarcodeWindow(self.barcode_1, figsize=self.figsize, dpi=self.dpi)
        elif which_barcode == "Barcode 2":
            PlotBarcodeWindow(self.barcode_2, figsize=self.figsize, dpi=self.dpi)

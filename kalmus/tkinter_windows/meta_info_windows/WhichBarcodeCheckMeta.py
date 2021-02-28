""" WhichBarcodeCheckMeta Class """

import tkinter
from kalmus.tkinter_windows.meta_info_windows.MetaInfoWindow import MetaInfoWindow
from kalmus.tkinter_windows.gui_utils import resource_path


class WhichBarcodeCheckMeta():
    """
    WhichBarcodeCheckMeta Class
    GUI window for user to choose which barcode to check with the meta information
    """
    def __init__(self, barcode_1, barcode_2, barcodes_stack):
        """
        Initialize

        :param barcode_1: The barcode 1
        :param barcode_2: The barcode 2
        :param barcodes_stack: The dictionary that stored all the barcode in memory
        """
        self.barcode_1 = barcode_1
        self.barcode_2 = barcode_2
        self.barcode_stacks = barcodes_stack

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Which Barcode to Check Meta Info")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Option variable
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

        # Check button
        self.button_check = tkinter.Button(master=self.window, text="Check", command=self.check_meta_info)
        self.button_check.grid(row=2, column=0, padx=50)

    def check_meta_info(self):
        """
        Get the selected option from user and instantiate the MetaInfoWindow using the given option (barcode)
        """
        # Get the selection
        which_barcode = self.barcode_option.get()

        # Quit current window
        self.window.destroy()

        # Instantiate the MetaInfoWindow using the selection
        if which_barcode == "Barcode 1":
            MetaInfoWindow(self.barcode_1, self.barcode_stacks)
        elif which_barcode == "Barcode 2":
            MetaInfoWindow(self.barcode_2, self.barcode_stacks)

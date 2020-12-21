""" MetaInfoWindow Class """

import tkinter
from kalmus.tkinter_windows.SpecifyMetaDataWindow import SpecifyMetaDataWindow
from kalmus.tkinter_windows.KALMUS_utils import resource_path

keys = ["Film Title", "Directors", "Country of Origin", "Produced Year", "Genre"]


class MetaInfoWindow():
    """
    MetaInfoWindow Class
    GUI window that displays the meta information of the selected barcode
    """
    def __init__(self, barcode, barcodes_stack):
        """
        Initialize
        :param barcode: The barcode to check with the meta information
        :param barcodes_stack: The dictionary that store all the barcodes on the memory
        """
        self.barcode = barcode
        self.barcodes_stack = barcodes_stack

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Barcode Meta Information")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Label prompt for the meta information display
        self.meta_info_label = tkinter.Label(self.window, text="", width=35, bg='white', anchor='w',
                                             justify=tkinter.LEFT)
        self.meta_info_label.grid(row=0, column=0, columnspan=2, sticky=tkinter.W)

        # Update the Meta information text
        self.refresh_text()

        # Button to refresh the displayed meta information of the barcode
        self.refresh_button = tkinter.Button(master=self.window, text="Refresh",
                                             command=self.refresh_text)
        self.refresh_button.grid(row=1, column=0)

        # Button to add/update meta information to the barcode
        self.add_info_button = tkinter.Button(master=self.window, text="Update Meta Info",
                                              command=self.update_meta_info)
        self.add_info_button.grid(row=1, column=1)

    def refresh_text(self):
        """
        Refresh the meta information text displayed for the barcode
        :return:
        """
        meta_text = "Meta Information of the Barcode:\n"

        # Build the text using the keys and their values stored in the barcodes's meta information dictionary
        if self.barcode.meta_data is not None:
            for key in keys:
                if key in self.barcode.meta_data.keys():
                    format_string = "{: <s}   {:s}\n".format(str(key) + ":", str(self.barcode.meta_data[key]))
                    meta_text += format_string
        self.meta_info_label["text"] = meta_text

    def update_meta_info(self):
        """
        Instantiate the SpecifyMetaDataWindow, if the user press the add info button
        :return:
        """
        SpecifyMetaDataWindow(self.barcode.__dict__["meta_data"], barcode=self.barcode,
                              barcode_stacks=self.barcodes_stack)

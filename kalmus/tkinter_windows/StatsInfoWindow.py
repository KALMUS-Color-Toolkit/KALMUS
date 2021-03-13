""" StatsInfoWindow Class """

import tkinter

from kalmus.tkinter_windows.gui_utils import get_comparison_result_text, resource_path


class StatsInfoWindow():
    """
    StatsInfoWindow Class
    Show the similarity scores between two barcodes using all comparing metrics
    The score are shown in text panel
    """
    def __init__(self, barcode_1, barcode_2):
        """
        Initialize the Window

        :param barcode_1: The barcode 1
        :param barcode_2: The barcode 2
        """
        self.barcode_1 = barcode_1
        self.barcode_2 = barcode_2

        # Initialize the window
        self.window = tkinter.Tk()

        self.window.configure(bg="#FFFFFF")
        self.window.wm_title("Barcodes Similarity Statistics")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Get the comparison result (in string) between two barcodes
        result_text = get_comparison_result_text(self.barcode_1, self.barcode_2)

        # Show the result in a Label (text panel)
        self.info_label = tkinter.Label(self.window, text=result_text, width=35, bg='white', anchor='w',
                                        justify=tkinter.LEFT)
        self.info_label.grid(row=0, column=0, rowspan=8)

""" SaveImageWindow Class """

import tkinter
from tkinter.messagebox import showerror, showinfo
import tkinter.filedialog
import matplotlib.pyplot as plt
import cv2
import os

from kalmus.tkinter_windows.gui_utils import resource_path


class SaveImageWindow():
    """
    SaveImageWindow Class
    Save the barcode into the image
    """
    def __init__(self, barcode_1, barcode_2):
        """
        Initialize
        :param barcode_1: The barcode 1
        :param barcode_2: The barcode 2
        """
        # Initialize the window
        self.window = tkinter.Tk()
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))
        self.window.wm_title("Save Image")

        self.barcode_1 = barcode_1
        self.barcode_2 = barcode_2

        # Label prompt for which barcode to save
        which_barcode_label = tkinter.Label(self.window, text="Barcode: ")
        which_barcode_label.grid(row=0, column=0, columnspan=1)

        # Barcode option variable
        self.barcode_option = tkinter.StringVar(self.window)
        self.barcode_option.set("Barcode 1")

        # Radio button for which barcode to save
        radio_barcode_1 = tkinter.Radiobutton(self.window, text="Barcode 1", variable=self.barcode_option,
                                              value="Barcode 1", command=self.update_size_entry)
        radio_barcode_1.grid(row=1, column=0)
        radio_barcode_1.select()

        radio_barcode_2 = tkinter.Radiobutton(self.window, text="Barcode 2", variable=self.barcode_option,
                                              value="Barcode 2", command=self.update_size_entry)
        radio_barcode_2.grid(row=2, column=0)

        # The width and height (in pixels) of the selected barcode
        width = self.barcode_1.get_barcode().shape[1]
        height = self.barcode_1.get_barcode().shape[0]

        # Resize the barcode into desirable size before saving
        self.resize_x_label = tkinter.Label(self.window, text="Saved Width (pixels): ")
        self.resize_x_label.grid(row=1, column=1, sticky=tkinter.E)

        self.resize_x_entry = tkinter.Entry(self.window, textvariable=-2, width=5)
        self.resize_x_entry.grid(row=1, column=2, padx=15, sticky=tkinter.W)
        self.resize_x_entry.insert(0, str(width))

        self.resize_y_label = tkinter.Label(self.window, text="Saved Height (pixels): ")
        self.resize_y_label.grid(row=2, column=1, sticky=tkinter.E)

        self.resize_y_entry = tkinter.Entry(self.window, textvariable=-3, width=5)
        self.resize_y_entry.grid(row=2, column=2, padx=15, sticky=tkinter.W)
        self.resize_y_entry.insert(0, str(height))

        # Label prompt for the file name (path) of the saved image
        filename_label = tkinter.Label(self.window, text="Image file path: ")
        filename_label.grid(row=3, column=0)

        # Text entry for user to specify the path of the saved image
        self.filename_entry = tkinter.Entry(self.window, textvariable="", width=40)
        self.filename_entry.grid(row=3, column=1, columnspan=1, sticky=tkinter.W)

        # Button to browse the location in a file manager window
        self.button_browse_folder = tkinter.Button(self.window, text="Browse", command=self.browse_folder)
        self.button_browse_folder.grid(row=3, column=2, sticky=tkinter.W)

        # Button to save the image into the given path using the given size
        self.button_save_image = tkinter.Button(master=self.window, text="Save Barcode", command=self.save_image)
        self.button_save_image.grid(row=4, column=0)

    def browse_folder(self):
        """
        Browse the folders in a file manager window
        """
        # Get the file name/path from the user input in the file manager
        filename = tkinter.filedialog.asksaveasfilename(initialdir=".", title="Save Image file",
                                                    filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"),
                                                               ("All files", "*.*")))

        # Update the file name/path to the file name entry
        self.filename_entry.delete(0, tkinter.END)
        self.filename_entry.insert(0, filename)

    def update_size_entry(self):
        """
        Update the size of current selected barcodes displayed in the resize entries
        """
        # Find the current selected barcode
        # Update the width and height (in pixels) of that barcode in the resize entries
        if self.barcode_option.get() == "Barcode 1":
            width = self.barcode_1.get_barcode().shape[1]
            height = self.barcode_1.get_barcode().shape[0]

        elif self.barcode_option.get() == "Barcode 2":
            width = self.barcode_2.get_barcode().shape[1]
            height = self.barcode_2.get_barcode().shape[0]

        self.resize_x_entry.delete(0, tkinter.END)
        self.resize_x_entry.insert(0, width)

        self.resize_y_entry.delete(0, tkinter.END)
        self.resize_y_entry.insert(0, height)

    def save_image(self):
        """
        Save the currently selected barcode into the image with the given size
        """
        # Check if the filename is given
        filename = self.filename_entry.get()
        if len(filename) == 0:
            showerror("File Name is Not Given", "Please specify the path to the saved image.")
            return

        # Get which barcode to save
        if self.barcode_option.get() == "Barcode 1":
            barcode = self.barcode_1.get_barcode().astype("uint8")
            barcode_type = self.barcode_1.barcode_type
        elif self.barcode_option.get() == "Barcode 2":
            barcode = self.barcode_2.get_barcode().astype("uint8")
            barcode_type = self.barcode_2.barcode_type

        # Resize the barcode into the desired shape (notice that the original barcode won't be affected)
        barcode = cv2.resize(barcode, dsize=(int(self.resize_x_entry.get()), int(self.resize_y_entry.get())),
                             interpolation=cv2.INTER_NEAREST)

        # Save the barcode with desirable color map based on its barcode type
        if barcode_type == "Color":
            plt.imsave(filename, barcode)
        else:
            plt.imsave(filename, barcode, cmap="gray")

        # Quit the window
        self.window.destroy()

        showinfo("Image Saved Successfully", "The image is saved successfully.\n\n"
                                             "The Path to the Image: {:20s}".format(os.path.abspath(filename)))

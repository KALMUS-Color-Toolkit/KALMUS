""" SaveBarcodeWindow Class """

import tkinter
import tkinter.filedialog
from tkinter.messagebox import showwarning, showinfo
import os

from kalmus.tkinter_windows.gui_utils import resource_path


class SaveBarcodeWindow():
    """
    SaveBarcodeWindow Class
    GUI window for user to select the barcode to save into a json file that can be later loaded back to kalmus
    """
    def __init__(self, barcode_stack):
        """
        Initialize

        :param barcode_stack: the dictionary that stored all the barcodes on the memory
        """
        self.barcode_stack = barcode_stack

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))
        self.window.wm_title("Save Barcode from Memory Stack")

        # List box that lists all the barcodes stored on the memory (shows the barcode's key in the dictionary)
        self.listbox = tkinter.Listbox(self.window, selectmode=tkinter.SINGLE, width=65, height=20)
        self.listbox.grid(row=0, column=0, columnspan=4)

        # List all the barcodes in the list box using their keys
        for barcode_names in self.barcode_stack.keys():
            self.listbox.insert(tkinter.END, barcode_names)

        # Label prompt for the file name/path to the saved json file
        filename_label = tkinter.Label(self.window, text="JSON file path: ")
        filename_label.grid(row=1, column=0)

        # Text entry for user to specify the file name/path to the saved json file
        self.filename_entry = tkinter.Entry(self.window, textvariable="", width=40)
        self.filename_entry.grid(row=1, column=1, columnspan=1, sticky=tkinter.W)

        # Button to browse the location in a file manager
        self.button_browse_folder = tkinter.Button(self.window, text="Browse", command=self.browse_folder)
        self.button_browse_folder.grid(row=1, column=2, sticky=tkinter.W)

        # Button to save the barcode into json file
        self.button_save = tkinter.Button(master=self.window, text="Save Barcode", command=self.save_stack)
        self.button_save.grid(row=2, column=0, sticky=tkinter.W)

    def browse_folder(self):
        """
        Browse the folders in a file manager window
        """
        # Get the file name/path from the user input in the file manager
        filename = tkinter.filedialog.asksaveasfilename(initialdir=".", title="Save JSON file",
                                                    filetypes=(("json files", "*.json"), ("txt files", "*.txt"),
                                                               ("All files", "*.*")))

        # Update the file name/path to the file name entry
        self.filename_entry.delete(0, tkinter.END)
        self.filename_entry.insert(0, filename)

    def save_stack(self):
        """
        Save the selected barcode from the memory stack to the json file
        """
        # Get the dictionary key of the selected barcode
        selected_barcode_names = [self.listbox.get(idx) for idx in self.listbox.curselection()]

        # Get the file name/path to the saved json file from the user input
        filename = self.filename_entry.get()

        if len(filename) == 0:
            showwarning("Default Saved JSON Path is Used", "Path to the saved JSON file is not specified.\n"
                                                           "Default save path is used.\n"
                                                           "File will be saved in the current working directory.\n"
                                                           "It is recommended to specify the file path.")
            filename = None

        # Saved the barcode
        for barcode_name in selected_barcode_names:
            barcode = self.barcode_stack[barcode_name]
            barcode.save_as_json(filename)

        # Quit the window
        self.window.destroy()

        # Show success message
        showinfo("JSON File Saved Successfully", "The JSON file is successfully saved.\n\n"
                                                 "The Path to the File: {:20s}".format(os.path.abspath(filename)))

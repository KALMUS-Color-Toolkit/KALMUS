""" SpecifyMetaDataWindow class """

import tkinter
import copy

from kalmus.tkinter_windows.gui_utils import resource_path

# Available genre options
genres = ["Comedy", "Drama", "Western", "Science Fiction", "War", "Melodrama", "Mystery/Thriller", "Action/Adventure",
          "Musical", "Romance", "Horror", "Other:"]


class SpecifyMetaDataWindow():
    """
    SpecifyMetaDataWindow Class
    GUI window for user to specify the meta information of the selected barcode
    """
    def __init__(self, meta_data_dict, barcode=None, barcode_stacks=None):
        """
        Initialize

        :param meta_data_dict: The meta information dictionary of the barcode
        :param barcode: The barcode
        :param barcode_stacks: The dictionary that stored all the barcode on memory
        """
        self.meta_data_dict = meta_data_dict
        self.barcode = barcode
        self.barcodes_stack = barcode_stacks

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Specify Meta Data")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Set up the label prompt for the film title specification
        self.title_label = tkinter.Label(self.window, text="Film Title:")
        self.title_label.grid(row=0, column=0, sticky=tkinter.W)

        # Set up the the entry for user to specify the barcode's film title
        self.title_entry = tkinter.Entry(self.window, textvariable="1", width=30)
        self.title_entry.grid(row=0, column=1, sticky=tkinter.W)

        # Set up the label prompt for the film director specification
        self.directory_label = tkinter.Label(self.window, text="Directors:")
        self.directory_label.grid(row=1, column=0, sticky=tkinter.W)

        # Set up the entry user to specify the film director
        self.directory_entry = tkinter.Entry(self.window, textvariable="2", width=30)
        self.directory_entry.grid(row=1, column=1, sticky=tkinter.W)

        # Set up the label prompt for the film's country of origin specification
        self.country_origin_label = tkinter.Label(self.window, text="Country of Origin:")
        self.country_origin_label.grid(row=2, column=0, sticky=tkinter.W)

        # Set up the entry for user to specify the film's country of origin
        self.country_origin_entry = tkinter.Entry(self.window, textvariable="3", width=30)
        self.country_origin_entry.grid(row=2, column=1, sticky=tkinter.W)

        # Set up the label prompt for the produced year specification
        self.year_label = tkinter.Label(self.window, text="Produced Year:")
        self.year_label.grid(row=3, column=0, sticky=tkinter.W)

        # Set up the entry for user to specify the produced year of the film
        self.year_entry = tkinter.Entry(self.window, textvariable="4", width=30)
        self.year_entry.grid(row=3, column=1, sticky=tkinter.W)

        # Set up the label prompt for the film genre specification
        self.genre_label = tkinter.Label(self.window, text="Genre:")
        self.genre_label.grid(row=4, column=0, sticky=tkinter.W)

        # Genre variable
        self.genre_var = tkinter.StringVar(self.window)
        self.genre_var.set("Comedy")
        self.genre_var.trace("w", callback=self.update_other_entry)

        # Genre dropdown list
        self.genre_dropdown = tkinter.OptionMenu(self.window, self.genre_var, *genres)
        self.genre_dropdown.grid(row=4, column=1, sticky=tkinter.W)

        # Other genre entry for user to specify a non-specified (custom) genre
        self.other_entry = tkinter.Entry(self.window, textvariable="5", width=8, state="disabled")
        self.other_entry.grid(row=4, column=2, sticky=tkinter.W)

        # Update the meta data button
        self.update_meta_button = tkinter.Button(master=self.window, text="Update Meta Info",
                                                 command=self.update_meta_info)
        self.update_meta_button.grid(row=5, column=1)

    def update_meta_info(self):
        """
        Update the meta information of the barcode using user input
        """
        # Get the user input
        title = self.title_entry.get()
        director = self.directory_entry.get()
        country_of_origin = self.country_origin_entry.get()
        year = self.year_entry.get()
        genre = self.genre_var.get()

        # For non empty input
        # Update the data to the corresponding key in the meta data dictionary
        if len(title) != 0:
            self.meta_data_dict["Film Title"] = copy.deepcopy(title)
        if len(director) != 0:
            self.meta_data_dict["Directors"] = copy.deepcopy(director)
        if len(country_of_origin) != 0:
            self.meta_data_dict["Country of Origin"] = copy.deepcopy(country_of_origin)
        if len(year) != 0:
            self.meta_data_dict["Produced Year"] = copy.deepcopy(year)
        if genre != "Other:":
            self.meta_data_dict["Genre"] = copy.deepcopy(genre)
        else:
            if len(self.other_entry.get()) != 0:
                self.meta_data_dict["Genre"] = copy.deepcopy(self.other_entry.get())
            else:
                self.meta_data_dict["Genre"] = copy.deepcopy("Other")

        # If the barcode is given, update the meta data dictionary to the barcode's attributes
        if self.barcode is not None:
            self.barcode.__dict__["meta_data"] = copy.deepcopy(self.meta_data_dict)

        # If the memory stack of the barcode is given, update the barcode to the memory stack
        if self.barcodes_stack is not None:
            key_barcode = str(title) + "_" + str(director) + "_" + str(country_of_origin)\
                          + "_" + str(year) + "_" + str(genre) + "_modified_meta_info"
            self.barcodes_stack[key_barcode] = copy.deepcopy(self.barcode)

        # Quit the window
        self.window.destroy()

    def update_other_entry(self, *args):
        """
        Enable the other genre entry once user select Other: in the dropdown list

        :param args: required by the tkinter callback
        """
        # Enable or disable the other genre entry based on the dropdown list selection
        if self.genre_var.get() == "Other:":
            self.other_entry.config(state="normal")
        else:
            self.other_entry.config(state="disabled")

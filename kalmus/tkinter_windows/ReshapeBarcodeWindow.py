""" ReshapeBarcodeWindow Class """

import tkinter
import copy
import cv2

from kalmus.tkinter_windows.gui_utils import update_graph, resource_path


class ReshapeBarcodeWindow():
    """
    ReshapeBarcodeWindow Class
    GUI window for user to reshape the selected barcode into the desirable shape
    """
    def __init__(self, barcode_1, barcode_2, axes, canvas):
        """
        Initialize

        :param barcode_1: The barcode 1
        :param barcode_2: The barcode 2
        :param axes: The display axes in the MainWindow of the kalmus
        :param canvas: The display canvas in the MainWindow of the kalmus
        """
        self.barcode_1 = barcode_1
        self.barcode_2 = barcode_2

        self.axes = axes
        self.canvas = canvas

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Reshape/Resize Barcode Config")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Reshape/Resize option
        self.config_option = tkinter.StringVar(self.window)
        self.config_option.set("Reshape")  # initialize

        # Prompt for the resize parameters specification
        params_label = tkinter.Label(self.window, text="Config Params: ")
        params_label.grid(row=0, column=0, columnspan=1, sticky=tkinter.W)

        # Label (text) prompt and entry for user to specify the resize parameters
        column_length_label = tkinter.Label(self.window, text="Frames per Column: ")
        column_length_label.grid(row=1, column=0, sticky=tkinter.W)

        self.column_length_entry = tkinter.Entry(self.window, textvariable="-1", width=5)
        self.column_length_entry.grid(row=1, column=1, padx=15)

        self.resize_x_label = tkinter.Label(self.window, text="Scale Width by (ratio):    ")
        self.resize_x_label.grid(row=2, column=0, sticky=tkinter.W)

        self.resize_x_entry = tkinter.Entry(self.window, textvariable="-2", width=5, state="disabled")
        self.resize_x_entry.grid(row=2, column=1, padx=15)

        self.resize_y_label = tkinter.Label(self.window, text="Scale Height by (ratio):    ")
        self.resize_y_label.grid(row=3, column=0, sticky=tkinter.W)

        self.resize_y_entry = tkinter.Entry(self.window, textvariable="-3", width=5, state="disabled")
        self.resize_y_entry.grid(row=3, column=1, padx=15)

        # Label prompt for displaying the width and height of the currently selected barcode
        self.size_label = tkinter.Label(self.window, text="Current Width = {:d}\nCurrent Height = {:d}"
                                        .format(self.barcode_1.get_barcode().shape[1],
                                                self.barcode_1.get_barcode().shape[0]))
        self.size_label.grid(row=4, column=0, columnspan=1)

        # Button to process the resize
        self.process_button = tkinter.Button(self.window, text="Process", command=self.reshape_resize_barcode)
        self.process_button.grid(row=4, column=2, sticky=tkinter.W)

        # Label prompt for the Resize type selection
        config_label = tkinter.Label(self.window, text="Config options: ")
        config_label.grid(row=0, column=2, columnspan=1)

        # Radio button for selecting the resize type
        radio_reshape = tkinter.Radiobutton(self.window, text="Reshape", variable=self.config_option,
                                            value="Reshape", anchor='w',
                                            command=self.reshape)
        radio_reshape.grid(row=1, column=2, sticky=tkinter.W)
        radio_reshape.select()

        radio_scaling = tkinter.Radiobutton(self.window, text="Scaling", variable=self.config_option,
                                            value="Scaling", anchor='w',
                                            command=self.scale)
        radio_scaling.grid(row=2, column=2, sticky=tkinter.W)

        radio_resize = tkinter.Radiobutton(self.window, text="Resize", variable=self.config_option,
                                           value="Resize", anchor='w',
                                           command=self.resize)
        radio_resize.grid(row=3, column=2, sticky=tkinter.W)

        # Label prompt for selecting which barcode to resize
        which_barcode_label = tkinter.Label(self.window, text="Barcode: ")
        which_barcode_label.grid(row=0, column=3, columnspan=1)

        # Option variable
        self.barcode_option = tkinter.StringVar(self.window)
        self.barcode_option.set("Barcode 1")

        # Radio button for selecting which barcode to resize
        radio_barcode_1 = tkinter.Radiobutton(self.window, text="Barcode 1", variable=self.barcode_option,
                                              value="Barcode 1", command=self.update_size_label)
        radio_barcode_1.grid(row=1, column=3)
        radio_barcode_1.select()

        radio_barcode_2 = tkinter.Radiobutton(self.window, text="Barcode 2", variable=self.barcode_option,
                                              value="Barcode 2", command=self.update_size_label)
        radio_barcode_2.grid(row=2, column=3)

    def update_size_label(self):
        """
        Update the size label if the currently selected barcode is changed
        """
        if self.barcode_option.get() == "Barcode 1":
            text = "Current Width = {:d}\nCurrent Height = {:d}".format(
                self.barcode_1.get_barcode().shape[1], self.barcode_1.get_barcode().shape[0])
        elif self.barcode_option.get() == "Barcode 2":
            text = "Current Width = {:d}\nCurrent Height = {:d}".format(
                self.barcode_2.get_barcode().shape[1], self.barcode_2.get_barcode().shape[0])

        self.size_label['text'] = text

    def reshape(self):
        """
        Enable or disable the input parameters entry if the reshape radio button is selected
        """
        self.column_length_entry.config(state='normal')
        self.resize_x_entry.config(state='disabled')
        self.resize_y_entry.config(state='disabled')

    def scale(self):
        """
        Enable or disable the input parameters entry and update the corresponding text
        if the scale radio button is selected
        """
        self.resize_x_label['text'] = "Scale Width by (ratio):    "
        self.resize_y_label['text'] = "Scale Height by (ratio):    "

        self.column_length_entry.config(state='disabled')
        self.resize_x_entry.config(state='normal')
        self.resize_y_entry.config(state='normal')

    def resize(self):
        """
        Enable or disable the input parameters entry and update the corresponding text
        if the resize radio button is selected
        """
        self.resize_x_label['text'] = "Resize Width to (pixels): "
        self.resize_y_label['text'] = "Resize Height to (pixels): "

        self.column_length_entry.config(state='disabled')
        self.resize_x_entry.config(state='normal')
        self.resize_y_entry.config(state='normal')

    def reshape_resize_barcode(self):
        """
        Reshape or resize the barcode using the given parameters
        """
        # Get the reshape/resize type from the user selection
        option = self.config_option.get()

        # Get which barcode to reshape/resize
        if self.barcode_option.get() == "Barcode 1":
            barcode = self.barcode_1
        elif self.barcode_option.get() == "Barcode 2":
            barcode = self.barcode_2

        # Save the current barcode size
        old_barcode_size = barcode.get_barcode().shape[0] * barcode.get_barcode().shape[1]

        # Reshape/resize the currently selected barcode using the given type with parameters
        if option == "Reshape":
            frames_per_column_str = self.column_length_entry.get()

            # Check if the reshape parameter is given
            # If not given, return and do not process the reshape
            if len(frames_per_column_str) == 0:
                return

            frames_per_column = int(frames_per_column_str)
            barcode.reshape_barcode(frames_per_column)

            self.update_scale_factor(barcode, old_barcode_size)
            self.updated_new_barcode()
        elif option == "Resize":
            barcode_shape = barcode.get_barcode().shape
            resize_x, resize_y = self._check_resize_entry(barcode_shape[1], barcode_shape[0])
            if resize_x is None:
                return

            resized_barcode = cv2.resize(barcode.get_barcode(),
                                         dsize=(int(resize_x), int(resize_y)),
                                         interpolation=cv2.INTER_NEAREST)
            barcode.barcode = resized_barcode

            self.update_scale_factor(barcode, old_barcode_size)
            self.updated_new_barcode()
        elif option == "Scaling":
            resize_x, resize_y = self._check_resize_entry(1, 1)
            if resize_x is None:
                return

            resized_barcode = cv2.resize(barcode.get_barcode(),
                                         dsize=(0, 0),
                                         fx=float(resize_x),
                                         fy=float(resize_y),
                                         interpolation=cv2.INTER_NEAREST)
            barcode.barcode = resized_barcode

            self.update_scale_factor(barcode, old_barcode_size)
            self.updated_new_barcode()

        # Quit the window
        self.window.destroy()

    def _check_resize_entry(self, default_x, default_y):
        """
        Check if the resize parameter is given
        If one of the parameter is not given assume that dimension is unchanged
        If both are not given, return and do not process the resize.

        :param default_x: Default x dimension
        :param default_y: Default y dimension
        :return: Processed resize x and y parameters from the user input
        """
        resize_x_str = self.resize_x_entry.get()
        resize_y_str = self.resize_y_entry.get()

        if len(resize_x_str) == 0 and len(resize_y_str) == 0:
            return None, None
        if len(resize_x_str) == 0:
            resize_x = str(default_x)
        else:
            resize_x = resize_x_str
        if len(resize_y_str) == 0:
            resize_y = str(default_y)
        else:
            resize_y = resize_y_str

        return resize_x, resize_y

    def update_scale_factor(self, barcode, old_barcode_size):
        """
        Update the scale factor of the barcode

        :param barcode: The barcode to update
        :param old_barcode_size: The old size of that barcode
        """
        barcode.scale_factor *= (old_barcode_size / (barcode.get_barcode().shape[0] * barcode.get_barcode().shape[1]))

    def updated_new_barcode(self):
        """
        Update the resized/reshaped barcode to the MainWindow of the kalmus
        """
        # Clear the display axes
        self.axes[0][0].cla()
        self.axes[1][0].cla()
        self.axes[0][1].cla()
        self.axes[1][1].cla()

        # Update the displayed barcode and redraw the canvas
        if self.barcode_1.get_barcode().shape[1] > self.barcode_2.get_barcode().shape[1]:
            temp = copy.deepcopy(self.barcode_1)

            self.barcode_1.__dict__ = self.barcode_2.__dict__.copy()
            self.barcode_2.__dict__ = temp.__dict__.copy()

        update_graph(barcode_1=self.barcode_1, barcode_2=self.barcode_2, axes=self.axes)

        # Redraw the canvas
        self.canvas.draw()

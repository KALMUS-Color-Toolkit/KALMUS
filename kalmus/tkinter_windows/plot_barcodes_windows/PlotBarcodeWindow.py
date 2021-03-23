"""
PlotBarcodeWindow Class
ColorHistogramWindow Class
RGBColorCubeWindow Class
OutputCSVWindow Class
"""

import tkinter
import tkinter.filedialog
from tkinter.messagebox import showinfo, showerror

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import os

from kalmus.utils.visualization_utils import show_colors_in_cube
from kalmus.tkinter_windows.gui_utils import resource_path, update_hist
import kalmus.utils.artist
from skimage.color import rgb2hsv
import pandas as pd


class PlotBarcodeWindow():
    """
    PlotBarcodeWindow Class
    GUI window of plotting the barcode for user to inspect in details
    """
    def __init__(self, barcode, figsize=(6, 4), dpi=100):
        """
        Initialize

        :param barcode: The barcode that will be inspected
        :param figsize: The size of the plotted figure
        :param dpi: The dpi of the figure
        """
        self.barcode = barcode

        # Initialize the window
        self.plot_window = tkinter.Tk()
        self.plot_window.wm_title("Inspect Barcode")
        self.plot_window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Set up the plotted figure
        self.fig = plt.figure(figsize=figsize, dpi=dpi)

        # Use the correct color map based on the input barcode's type
        if barcode.barcode_type == "Brightness":
            plt.imshow(barcode.get_barcode().astype("uint8"), cmap="gray")
        else:
            plt.imshow(barcode.get_barcode().astype("uint8"))
        plt.axis("off")
        plt.tight_layout()

        # Set up the canvas for the figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)  # A tk.DrawingArea.
        self.canvas.draw()

        # Dynamic layout based on the type of the inspected barcode
        if barcode.barcode_type == "Color":
            column_span = 3
        else:
            column_span = 2
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=column_span, pady=3)

        # Use tkinter Frame to organize the figure widget
        toolbarFrame = tkinter.Frame(master=self.plot_window)
        toolbarFrame.grid(row=2, column=0, columnspan=column_span, sticky=tkinter.W, pady=6)

        # Initialize the plotting tool bar
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
        self.toolbar.update()

        # Button to output the data in the barcode to a csv file
        self.button_output_csv = tkinter.Button(master=self.plot_window, text="Output CSV",
                                                command=self.output_csv)
        self.button_output_csv.grid(row=1, column=0, padx=18)

        # Button to check the histogram distribution of the barcode's hue/brightness value
        self.button_hist = tkinter.Button(master=self.plot_window, text="Show Histogram",
                                              command=self.show_color_histogram)
        self.button_hist.grid(row=1, column=1, padx=14)

        # If the barcode is a color barcode, allow user to inspect the RGB color distribution in a RGB cube
        if barcode.barcode_type == "Color":
            self.button_cube = tkinter.Button(master=self.plot_window, text="Show Color in RGB Cube",
                                              command=self.show_RGB_color_in_cube)
            self.button_cube.grid(row=1, column=2)

    def show_RGB_color_in_cube(self):
        """
        Instantiate the RGBColorCubeWindow if user press the show color in RGB cube button
        """
        RGBColorCubeWindow(self.barcode)

    def show_color_histogram(self):
        """
        Instantiate the ColorHistogramWindow if user press the show histogram button
        """
        ColorHistogramWindow(self.barcode)

    def output_csv(self):
        OutputCSVWindow(self.barcode)


class ColorHistogramWindow():
    """
    ColorHistogramWindow Class
    GUI window that show the distribution of the barcode's hue[0, 360]/brightness[0, 255] value
    """
    def __init__(self, barcode):
        """
        Initialize

        :param barcode: The input barcode
        """
        # Set up the window
        self.window = tkinter.Tk()
        self.window.wm_title("Histogram Distribution")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Set up the plotted figure
        fig, ax = plt.subplots(figsize=(9, 5))

        update_hist(barcode, ax=ax, bin_step=5)

        # Plot the histogram based on the barcode's type
        if barcode.barcode_type == "Color":
            ax.set_xticks(np.arange(0, 361, 30))
            ax.set_xlabel("Color Hue (0 - 360)")
            ax.set_ylabel("Number of frames")
        else:
            ax.set_xticks(np.arange(0, 255, 15))
            ax.set_xlabel("Brightness (0 - 255)")
            ax.set_ylabel("Number of frames")

        # Set up the canvas of the figure
        canvas = FigureCanvasTkAgg(fig, master=self.window)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # Set up the tool bar of the figure
        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

class RGBColorCubeWindow():
    """
    RGBColorCubeWindow Class
    GUI window that shows the distribution of the barcode's RGB color in a RGB cube
    range in [0, 255] for all three channels
    """
    def __init__(self, barcode):
        """
        Initialize

        :param barcode: The input barcode
        """
        self.barcode = barcode

        # Set up the window
        self.window = tkinter.Tk()
        self.window.wm_title("Colors in RGB cube")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Set up the plotted figure
        sampling = 6000
        if sampling > self.barcode.colors.shape[0]:
            sampling = self.barcode.colors.shape[0]
        fig, ax = show_colors_in_cube(self.barcode.colors, return_figure=True, figure_size=(6, 6), sampling=sampling)

        # Set up the canvas
        canvas = FigureCanvasTkAgg(fig, master=self.window)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # Allow mouse events on 3D figure
        ax.mouse_init()

        # Set up the tool bar of the figure
        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


class OutputCSVWindow():
    """
    OutputCSVWindow class
    GUI window that outputs the per frame level color/brightness data of the inspected barcode
    The data output are stored in the csv file, and the data frame depends on the type of the barcode
    """
    def __init__(self, barcode):
        """
        Initialize

        :param barcode: The barcode to output the per frame level data
        """
        self.barcode = barcode

        # Set up the window
        self.window = tkinter.Tk()
        self.window.wm_title("Output the barcode to CSV")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Label prompt for the file name/path to the csv file
        filename_label = tkinter.Label(self.window, text="CSV file path: ")
        filename_label.grid(row=0, column=0, sticky=tkinter.W)

        # Text entry for user to type the file name/path to the csv file
        self.filename_entry = tkinter.Entry(self.window, textvariable="", width=40)
        self.filename_entry.grid(row=0, column=1, columnspan=1, sticky=tkinter.W)

        # Button to browse the folder
        self.button_browse_folder = tkinter.Button(self.window, text="Browse", command=self.browse_folder)
        self.button_browse_folder.grid(row=0, column=2)

        # Button to build/load the barcode using the given json file
        self.button_build_barcode = tkinter.Button(self.window, text="Output", command=self.output_csv_file)
        self.button_build_barcode.grid(row=1, column=1, columnspan=1)

    def output_csv_file(self):
        """
        Output the per frame level data to a csv file
        """
        # Get the file name of the output csv file
        csv_filename = self.filename_entry.get()

        if len(csv_filename) == 0:
            showerror("Invalid Path or Filename", "Please specify the path/filename of the generated csv file.\n")
            return

        # Get the sampled frame rate of the barcode
        sample_rate = self.barcode.sampled_frame_rate

        # Get the starting/skipped over frame of the barcode
        starting_frame = self.barcode.skip_over

        # Generate the corresponding csv file for the type of the barcode
        if self.barcode.barcode_type == 'Color':
            # Data frame of the csv file for the color barcode
            colors = self.barcode.colors
            hsvs = rgb2hsv(colors.reshape(-1, 1, 3).astype("float64") / 255)
            hsvs[..., 0] = 360 * hsvs[..., 0]
            colors = colors.astype("float64")
            brightness = 0.299 * colors[..., 0] + 0.587 * colors[..., 1] + 0.114 * colors[..., 1]

            colors = colors.astype("uint8")
            hsvs = hsvs.reshape(-1, 3)
            brightness = brightness.astype("int64")

            frame_indexes = np.arange(starting_frame, len(colors) * sample_rate + starting_frame, sample_rate)

            dataframe = pd.DataFrame(data={'Frame index': frame_indexes,
                                           'Red (0-255)': colors[..., 0],
                                           'Green (0-255)': colors[..., 1],
                                           'Blue (0-255)': colors[..., 2],
                                           'Hue (0 -360)': (hsvs[..., 0]).astype("int64"),
                                           'Saturation (0 - 1)': hsvs[..., 1],
                                           'Value (lightness) (0 - 1)': hsvs[..., 2],
                                           'Brightness': brightness})

        elif self.barcode.barcode_type == 'Brightness':
            # Data frame of the csv file for the brightness barcode
            brightness = self.barcode.brightness

            frame_indexes = np.arange(starting_frame, len(brightness) * sample_rate + starting_frame, sample_rate)
            # Get the per frame level brightness data
            dataframe = pd.DataFrame(data={'Frame index': frame_indexes,
                                           'Brightness': brightness.astype("uint8").reshape(-1)})

        dataframe = dataframe.set_index('Frame index')

        dataframe.to_csv(csv_filename)

        # Quit the window after outputting csv file
        self.window.destroy()

        showinfo("CSV File Generated Successfully", "CSV file has been generated successfully.\n"
                                                    "Path to the File: {:20s}".format(os.path.abspath(csv_filename)))

    def browse_folder(self):
        """
        Browse the folder to locate the json file
        """
        # Get the file name from the user selection
        filename = tkinter.filedialog.asksaveasfilename(initialdir=".", title="Select CSV file",
                                                      filetypes=(("csv files", "*.csv"), ("txt files", "*.txt"),
                                                                 ("All files", "*.*")))

        # Update the file name to the file name text entry
        self.filename_entry.delete(0, tkinter.END)
        self.filename_entry.insert(0, filename)

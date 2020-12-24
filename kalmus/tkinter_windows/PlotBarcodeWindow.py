"""
PlotBarcodeWindow Class
ColorHistogramWindow Class
RGBColorCubeWindow Class
OutputCSVWindow Class
"""

import tkinter
import tkinter.filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np

from kalmus.visualization_utils import show_colors_in_cube
from kalmus.tkinter_windows.KALMUS_utils import resource_path, update_hist
import kalmus.Artist
from skimage.color import rgb2hsv


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

        # Set up the canvas for the figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # Initialize the plotting tool bar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_window)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # Button to output the data in the barcode to a csv file
        self.button_output_csv = tkinter.Button(master=self.plot_window, text="Output CSV",
                                                command=self.output_csv)
        self.button_output_csv.pack(side=tkinter.BOTTOM)

        # If the barcode is a color barcode, allow user to inspect the RGB color distribution in a RGB cube
        if barcode.barcode_type == "Color":
            self.button_cube = tkinter.Button(master=self.plot_window, text="Show Color in RGB Cube",
                                              command=self.show_RGB_color_in_cube)
            self.button_cube.pack(side=tkinter.BOTTOM)

        # Button to check the histogram distribution of the barcode's hue/brightness value
        self.button_hist = tkinter.Button(master=self.plot_window, text="Show Histogram",
                                              command=self.show_color_histogram)
        self.button_hist.pack(side=tkinter.BOTTOM)

        # Start the window
        self.plot_window.mainloop()

    def show_RGB_color_in_cube(self):
        """
        Instantiate the RGBColorCubeWindow if user press the show color in RGB cube button
        :return:
        """
        RGBColorCubeWindow(self.barcode)

    def show_color_histogram(self):
        """
        Instantiate the ColorHistogramWindow if user press the show histogram button
        :return:
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

        # Start the window
        self.window.mainloop()


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

        # Start the window
        self.window.mainloop()


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
        :return:
        """
        # Get the file name of the output csv file
        csv_filename = self.filename_entry.get()

        # Get the sampled frame rate of the barcode
        sample_rate = self.barcode.sampled_frame_rate

        # Get the starting/skipped over frame of the barcode
        starting_frame = self.barcode.skip_over

        # Generate the corresponding csv file for the type of the barcode
        if self.barcode.barcode_type == 'Color':
            # Data frame of the csv file for the color barcode
            data_frame = ['Frame index', 'Red (0-255)', 'Green (0-255)', 'Blue (0-255)', 'Hue (0 -360)',
                          'Saturation (0 - 1)', 'Value (lightness) (0 - 1)','Brightness']
            kalmus.Artist.write_in_info(data_frame, csv_filename, mode='w')

            cur_frame = starting_frame
            # Get the per frame level color data
            for color in self.barcode.colors:
                r = int(color[0])
                g = int(color[1])
                b = int(color[2])
                brightness = int(0.299 * r + 0.587 * g + 0.114 * b)
                hsv = rgb2hsv(color.reshape(1, 1, -1).astype("float64") / 255)[0, 0]
                h = int(hsv[0] * 360)
                s = float(hsv[1])
                v = float(hsv[2])

                kalmus.Artist.write_in_info([cur_frame, r, g, b, h, s, v, brightness], csv_filename)

                cur_frame += sample_rate

        elif self.barcode.barcode_type == 'Brightness':
            # Data frame of the csv file for the brightness barcode
            data_frame = ['Frame index', 'Brightness']
            kalmus.Artist.write_in_info(data_frame, csv_filename, mode='w')

            cur_frame = starting_frame
            # Get the per frame level brightness data
            for bri in self.barcode.brightness:
                kalmus.Artist.write_in_info([cur_frame, int(bri[0])], csv_filename)

                cur_frame += sample_rate

        # Quit the window after outputting csv file
        self.window.destroy()

    def browse_folder(self):
        """
        Browse the folder to locate the json file
        :return:
        """
        # Get the file name from the user selection
        filename = tkinter.filedialog.asksaveasfilename(initialdir=".", title="Select CSV file",
                                                      filetypes=(("csv files", "*.csv"), ("txt files", "*.txt"),
                                                                 ("All files", "*.*")))

        # Update the file name to the file name text entry
        self.filename_entry.delete(0, tkinter.END)
        self.filename_entry.insert(0, filename)

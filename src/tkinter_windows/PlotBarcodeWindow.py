"""
PlotBarcodeWindow Class
ColorHistogramWindow Class
RGBColorCubeWindow Class
"""

import tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
from src.visualization_utils import show_colors_in_cube

from src.tkinter_windows.KALMUS_utils import resource_path, update_hist


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
        fig, ax = show_colors_in_cube(self.barcode.colors, return_figure=True, figure_size=(6, 6), sampling=8000)

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
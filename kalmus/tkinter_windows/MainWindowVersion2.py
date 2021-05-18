"""
MainWindow Class
Version2
"""

import tkinter
from tkinter.messagebox import askokcancel, showinfo, showerror

from kalmus.tkinter_windows.GenerateBarcodeWindow import GenerateBarcodeWindow
from kalmus.tkinter_windows.SaveBarcodeWindow import SaveBarcodeWindow
from kalmus.tkinter_windows.LoadStackWindow import LoadStackWindow
from kalmus.tkinter_windows.LoadJsonWindow import LoadJsonWindow
from kalmus.tkinter_windows.ReshapeBarcodeWindow import ReshapeBarcodeWindow
from kalmus.tkinter_windows.gui_utils import paint_hue_hist, update_axes_title, update_axes_ticks, resource_path
from kalmus.tkinter_windows.plot_barcodes_windows.WhichBarcodeInspectWindow import WhichBarcodeInspectWindow
from kalmus.tkinter_windows.StatsInfoWindow import StatsInfoWindow
from kalmus.tkinter_windows.SaveImageWindow import SaveImageWindow
from kalmus.tkinter_windows.meta_info_windows.WhichBarcodeCheckMeta import WhichBarcodeCheckMeta
from kalmus.tkinter_windows.time_points_windows.CheckTimePointWindow import CheckTimePointWindow

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

from skimage.color import rgb2hsv

import numpy as np

import copy
import matplotlib

# General setup of the figure
font = {'family': 'DejaVu Sans',
        'size': 8}

matplotlib.rc('font', **font)


class MainWindow():
    """
    MainWindow Class.
    The main GUI window for user to interact with the Kalmus software.
    Has two displays for the barcodes and the histograms of their hue/brightness values.
    Has all buttons to the subwindow of the kalmus software.
    """

    def __init__(self, barcode_tmp, barcode_gn, figsize=(12, 5), dpi=100):
        """
        Initialize

        :param barcode_tmp: The temporary barcode object for software initialization
        :param barcode_gn: The barcode generator object
        :param figsize: The size of the plotted figure
        :param dpi: The dpi of the plotted figure
        """
        # Initialize the barcode memory stack
        self.barcodes_stack = {"default": copy.deepcopy(barcode_tmp)}

        # Copy over the barcodes
        self.barcode_1 = copy.deepcopy(barcode_tmp)
        self.barcode_2 = copy.deepcopy(barcode_tmp)

        # Initialize the barcode's meta data to none
        self.barcode_1.meta_data = {}
        self.barcode_2.meta_data = {}

        # Get the barcode generator
        self.barcode_gn = barcode_gn

        # Initialize the window
        self.root = tkinter.Tk()

        self.root.configure(bg='#85C1FA')
        self.root.wm_title("KALMUS Version 1.3.9")
        self.root.iconbitmap(resource_path("kalmus_icon.ico"))

        # Initialize the figure
        self.fig, self.ax = plt.subplots(2, 2, figsize=figsize, dpi=dpi,
                                         gridspec_kw={'width_ratios': [2.8, 1]}, sharex='col', sharey='col')

        update_axes_title(self.ax, self.barcode_1, self.barcode_2)

        # Plot the barcodes into the figure
        self.barcode_display_1 = self.ax[0][0].imshow(self.barcode_1.get_barcode().astype("uint8"))
        self.barcode_display_2 = self.ax[1][0].imshow(self.barcode_2.get_barcode().astype("uint8"))

        # Normalize the barcode before converting the color map
        normalized_barcode_1 = self.barcode_1.get_barcode().astype("float") / 255

        hsv_colors_1 = rgb2hsv(normalized_barcode_1.reshape(-1, 1, 3))
        hue_1 = hsv_colors_1[..., 0] * 360

        # The step of the histogram
        bin_step = 5
        N, bins, patches = self.ax[0][1].hist(hue_1[:, 0], bins=(np.arange(0, 361, bin_step)))

        paint_hue_hist(bin_step, patches)

        # Update the hue histogram
        self.ax[0][1].set_xticks(np.arange(0, 361, 30))
        self.ax[0][1].set_xlabel("Color Hue (0 - 360)")
        self.ax[0][1].set_ylabel("Number of frames")

        normalized_barcode_2 = self.barcode_2.get_barcode().astype("float") / 255

        hsv_colors_2 = rgb2hsv(normalized_barcode_2.reshape(-1, 1, 3))
        hue_2 = hsv_colors_2[..., 0] * 360

        N, bins, patches = self.ax[1][1].hist(hue_2[:, 0], bins=(np.arange(0, 361, bin_step)))

        # Paint the hue histogram where each bin of the histogram is in the color of the corresponding hue
        paint_hue_hist(bin_step, patches)

        self.ax[1][1].set_xticks(np.arange(0, 361, 30))
        self.ax[1][1].set_xlabel("Color Hue (0 - 360)")
        self.ax[1][1].set_ylabel("Number of frames")

        # Use tight layout
        plt.tight_layout()

        update_axes_ticks(self.barcode_1, self.barcode_2, self.ax)

        # Draw the canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.draw()

        self.canvas.mpl_connect('button_press_event', self.time_pick)

        # Use tkinter Frame to organize the figure widget
        toolbarFrame = tkinter.Frame(master=self.root)
        toolbarFrame.grid(row=8, column=2)

        # Set up the tool bar of the plotted figure
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
        self.toolbar.update()

        # Position the canvas/plotted figure into the window
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=8, columnspan=3)

        self.generate_window_opened = False

        # Button to generate the barcode
        button_generate = tkinter.Button(master=self.root, text="Generate Barcode",
                                         command=self.generate_barcode)
        button_generate.grid(row=0, column=0, padx=3)

        # Button to load the barcode from existed json files
        button_load = tkinter.Button(master=self.root, text="Load JSON",
                                     command=self.load_json_barcode)
        button_load.grid(row=1, column=0)

        # Button to load the barcode from the memory stack
        button_load_stack = tkinter.Button(master=self.root, text="Load Memory",
                                           command=self.load_stack_barcode)
        button_load_stack.grid(row=2, column=0)

        # Button to reshape the barcode displayed in the main window
        button_reshape_barcode = tkinter.Button(master=self.root, text="Reshape Barcode",
                                                command=self.reshape_barcode)
        button_reshape_barcode.grid(row=3, column=0)

        # Button to save the barcode into json files
        button_save_json = tkinter.Button(master=self.root, text="Save JSON",
                                          command=self.save_barcode_on_stack)
        button_save_json.grid(row=4, column=0)

        # Button to save the barcode displayed into the image
        button_save_image = tkinter.Button(master=self.root, text="Save Image",
                                           command=self.save_image_from_display)
        button_save_image.grid(row=5, column=0)

        # Button to inspect the barcode in details
        button_barcode = tkinter.Button(master=self.root, text="Inspect Barcode",
                                        command=self.show_barcode)
        button_barcode.grid(row=6, column=0)

        # Button to show the statistics of the barcode
        button_stats_info = tkinter.Button(master=self.root, text="Stats Info",
                                           command=self.stats_info)
        button_stats_info.grid(row=7, column=0)

        # Button to quit the main window
        button_quit = tkinter.Button(master=self.root, text="Quit", command=self.close_window)
        button_quit.grid(row=8, column=0)

        # Button to check the meta data of the displayed barcodes
        button_check_meta = tkinter.Button(master=self.root, text="Check Meta Info", command=self.check_meta_info)
        button_check_meta.grid(row=8, column=3)

        # Close the window mainloop if user try to close the window
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        # Start the main window
        self.root.mainloop()

    def close_window(self):
        """
        close the Mainwindow.
        Check if the Generate Barcode window is still open before quiting the Main program.
        Return (cancel the quit) if the Generate Barcode window is still open.
        """
        # Check if generate barcode window is opened
        if self.generate_window_opened:
            # If it is opened show an error
            showerror("Generate Barcode Window is Opened", "Generate Barcode window is still opened!\n"
                                                           "Please close the Generate Barcode window before Quit.")
            return

        # Otherwise check if user want to quit the software
        quit_software = askokcancel("Quit KALMUS", "Are you sure you want to close the KALMUS?\n"
                                                   "All unsaved results will be lost.")
        # Quit if yes
        if quit_software:
            self.quit()

    def quit(self):
        """
        Quit the main window
        """
        self.root.quit()
        self.root.destroy()

    def check_meta_info(self):
        """
        Instantiate the WhichBarcodeCheckMeta window
        """
        WhichBarcodeCheckMeta(self.barcode_1, self.barcode_2, self.barcodes_stack)

    def show_barcode(self):
        """
        Instantiate the WhichBarcodeInspectWindow
        """
        WhichBarcodeInspectWindow(self.barcode_1, self.barcode_2, dpi=100, figsize=(7, 4))

    def load_json_barcode(self):
        """
        Instantiate the LoadJsonWindow
        """
        LoadJsonWindow(self.barcode_gn, self.barcode_1, self.barcode_2, self.ax,
                       self.canvas, self.barcodes_stack)

    def load_stack_barcode(self):
        """
        Instantiate the LoadStackWindow
        """
        LoadStackWindow(self.barcodes_stack, self.barcode_1, self.barcode_2, self.ax,
                        self.canvas)

    def reshape_barcode(self):
        """
        Instantiate the ReshapeBarcodeWindow
        """
        ReshapeBarcodeWindow(self.barcode_1, self.barcode_2, self.ax, self.canvas)

    def stats_info(self):
        """
        Instantiate the StatsInfoWindow
        """
        StatsInfoWindow(self.barcode_1, self.barcode_2)

    def generate_barcode(self):
        """
        Instantiate the GenerateBarcodeWindow
        """
        if not self.generate_window_opened:
            self.generate_window_opened = True
            GenerateBarcodeWindow(self.barcode_gn, self.barcodes_stack)
            self.generate_window_opened = False
        else:
            showinfo("Generate Barcode window is Opened", "Generate Barcode Window is already opened.")

    def save_barcode_on_stack(self):
        """
        Instantiate the SaveBarcodeWindow
        """
        SaveBarcodeWindow(self.barcodes_stack)

    def save_image_from_display(self):
        """
        Instantiate the SaveImageWindow
        """
        SaveImageWindow(self.barcode_1, self.barcode_2)

    def time_pick(self, event):
        """
        Pick the time at a point of the plotted barcode if user double click on that point

        :param event: matplotlib event. Only catch double click event
        """
        # If user is double click on the graph
        if event.dblclick:
            # Try get the x and y position of the clicked point
            try:
                ix, iy = int(event.xdata + 0.5), int(event.ydata + 0.5)
            except Exception:
                return

            # find which axis of the graph does the clicked point belong to
            for i, axe in enumerate(self.ax[:, 0]):
                if axe == event.inaxes:
                    # Check if it is plotted barcode 1 or plotted barcode 2
                    if i == 0:
                        barcode = self.barcode_1
                    else:
                        barcode = self.barcode_2

                    # Make sure the point is within the plotted barcode
                    barcode_shape = barcode.get_barcode().shape
                    if 0 <= iy < barcode_shape[0] and 0 <= ix < barcode_shape[1]:
                        # Instantiate the CheckTimePointWindow
                        CheckTimePointWindow(barcode, mouse_x=ix, mouse_y=iy)

""" DisplaySavedFramesWindow Class """

import tkinter

from kalmus.tkinter_windows.gui_utils import resource_path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np


class DisplaySavedFramesWindow():
    """
    DisplaySavedFramesWindow Class
    GUI window for displaying saved frame of a barcode around the clicked point
    """
    def __init__(self, barcode, mouse_x, mouse_y, figsize=(10, 2), dpi=100):
        self.barcode = barcode

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Display frames")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Set up the plotted figure
        self.fig = plt.figure(figsize=figsize, dpi=dpi)

        displayed_image = self.get_frames_image_for_display(mouse_x, mouse_y)
        plt.imshow(displayed_image)
        plt.axis("off")
        plt.tight_layout()

        # Set up the canvas for the figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # Initialize the plotting tool bar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.window)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    def get_frames_image_for_display(self, mouse_x, mouse_y):
        """
        Get the frames around the clicked point
        :param mouse_x: The x position of the clicked point
        :param mouse_y: The y position of the clicked point
        :return: The combined sampled frames for displaying
        """
        barcode_shape = self.barcode.get_barcode().shape
        # Get the middle position of the saved frame
        cur_pos = (mouse_x * barcode_shape[0] + mouse_y) / (barcode_shape[0] * barcode_shape[1])
        frame_pos = round(cur_pos * len(self.barcode.saved_frames))

        # Get another four frames around the middle frame
        # Make sure the frame positions/indexes are valid
        if frame_pos < 2:
            frame_pos = 2
        if frame_pos > len(self.barcode.saved_frames) - 3:
            frame_pos = len(self.barcode.saved_frames) - 3
        frames = self.barcode.saved_frames[frame_pos - 2: frame_pos + 3]

        # Get the combined five frames image
        combine_image = frames[0]
        for frame in frames[1:]:
            # Combine the frames into one image
            combine_image = np.concatenate((combine_image, frame), axis=1)

        return combine_image


""" CheckTimePointWindow Class """

import tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np

from kalmus.tkinter_windows.gui_utils import resource_path


class CheckTimePointWindow():
    """
    CheckTimePointWindow
    GUI window that shows the RGB/Brightness value, RGB color, x, y position, frame indexes and time
    at the clicked point
    """

    def __init__(self, barcode, mouse_x, mouse_y, figsize=(6, 0.7), dpi=100):
        """
        Initialize

        :param barcode: The barcode with clicked point
        :param mouse_x: The x position of the clicked point
        :param mouse_y: The y position of the clicked point
        """
        self.barcode = barcode
        self.x_pos = mouse_x
        self.y_pos = mouse_y

        # Compute the frame label
        frame = (self.barcode.skip_over + self.barcode.sampled_frame_rate * \
                ((self.x_pos * self.barcode.get_barcode().shape[0]) + self.y_pos)) * self.barcode.scale_factor
        frame = int(frame)

        # If frame rate is not given, use 30 as default
        if self.barcode.fps is None:
            self.barcode.fps = 30

        # Compute the time label
        time_tot_sec = frame / self.barcode.fps
        time_sec = int(time_tot_sec % 60)
        time_min = int((time_tot_sec / 60) % 60)
        time_hr = int(time_tot_sec / 3600)

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("At this point...")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))
        self.window.attributes('-topmost', True)

        # If the clicked barcode is color barcode
        if self.barcode.barcode_type == "Color":
            # Get the r, g, b value at that point
            r, g, b = barcode.get_barcode().astype("uint8")[self.y_pos, self.x_pos]
            # Set up the label
            color_r_label = tkinter.Label(master=self.window, text="Red: {:d}".format(r), fg='#9E1A1A')
            color_r_label.grid(row=0, column=0)

            color_g_label = tkinter.Label(master=self.window, text="Green: {:d}".format(g), fg='#028A0F')
            color_g_label.grid(row=0, column=1)

            color_b_label = tkinter.Label(master=self.window, text="Blue: {:d}".format(b), fg='#1520A6')
            color_b_label.grid(row=0, column=2)

            # Show the color
            color_label = tkinter.Label(master=self.window, text="", bg=f'#{r:02x}{g:02x}{b:02x}', width=6, height=2)
            color_label.grid(row=0, column=3, rowspan=2, padx=5, pady=5)
        elif self.barcode.barcode_type == "Brightness":
            # Get the brightness value (notices that r = g = b = brightness)
            r = g = b = barcode.get_barcode().astype("uint8")[self.y_pos, self.x_pos]
            brightness_value_label = tkinter.Label(master=self.window, text="Brightness: {:d}".format(r))
            brightness_value_label.grid(row=0, column=0, sticky=tkinter.E)

            # Set up the label
            brightness_label = tkinter.Label(master=self.window, text="", bg=f'#{r:02x}{g:02x}{b:02x}',
                                             width=12, height=1)
            # Show the brightness
            brightness_label.grid(row=0, column=1, columnspan=2, padx=5, pady=3)

        # Show the position
        pos_label = tkinter.Label(master=self.window, text="Position: ({:d}, {:d}) ".format(self.x_pos, self.y_pos))
        pos_label.grid(row=1, column=0)

        # Show the frame index
        self.frame_label = tkinter.Label(master=self.window, text="Frame: {:d} ".format(frame))
        self.frame_label.grid(row=1, column=1)

        # Show the time
        self.time_label = tkinter.Label(master=self.window, text="Time: {:02d}:{:02d}:{:02d} "
                                        .format(time_hr, time_min, time_sec))
        self.time_label.grid(row=1, column=2)

        if self.barcode.saved_frames is not None:
            # Set up the plotted figure
            self.fig = plt.figure(figsize=figsize, dpi=dpi)

            displayed_image = self.get_frames_image_for_display(mouse_x, mouse_y)
            plt.imshow(displayed_image)
            plt.axis('tight')
            plt.axis("off")
            plt.tight_layout()
            self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1)

            # Set up the canvas for the figure
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)  # A tk.DrawingArea.
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=2, column=0, rowspan=1, columnspan=4)

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

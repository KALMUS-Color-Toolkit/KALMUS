import tkinter
from tkinter.messagebox import showerror

from kalmus.tkinter_windows.KALMUS_utils import resource_path
from kalmus.tkinter_windows.CalibrateBarcodeTimeWindow import CalibrateBarcodeTimeWindow
from kalmus.tkinter_windows.DisplaySavedFramesWindow import DisplaySavedFramesWindow


class CheckTimePointWindow():
    def __init__(self, barcode, mouse_x, mouse_y):
        self.barcode = barcode
        self.x_pos = mouse_x
        self.y_pos = mouse_y

        frame = (self.barcode.skip_over + self.barcode.sampled_frame_rate * \
                ((self.x_pos * self.barcode.get_barcode().shape[0]) + self.y_pos)) * self.barcode.scale_factor
        frame = int(frame)

        if self.barcode.fps is None:
            self.barcode.fps = 29.8

        time_tot_sec = frame / self.barcode.fps
        time_sec = int(time_tot_sec % 60)
        time_min = int((time_tot_sec / 60) % 60)
        time_hr = int(time_tot_sec / 3600)

        self.window = tkinter.Tk()
        self.window.wm_title("At this point...")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        if self.barcode.barcode_type == "Color":
            r, g, b = barcode.get_barcode().astype("uint8")[self.y_pos, self.x_pos]
            color_r_label = tkinter.Label(master=self.window, text="Red: {:d}".format(r), fg='#9E1A1A')
            color_r_label.grid(row=0, column=0)

            color_g_label = tkinter.Label(master=self.window, text="Green: {:d}".format(g), fg='#028A0F')
            color_g_label.grid(row=0, column=1)

            color_b_label = tkinter.Label(master=self.window, text="Blue: {:d}".format(b), fg='#1520A6')
            color_b_label.grid(row=0, column=2)

            color_label = tkinter.Label(master=self.window, text="", bg=f'#{r:02x}{g:02x}{b:02x}', width=6, height=2)
            color_label.grid(row=0, column=3, rowspan=2, padx=5, pady=5)
        elif self.barcode.barcode_type == "Brightness":
            r = g = b = barcode.get_barcode().astype("uint8")[self.y_pos, self.x_pos]
            brightness_value_label = tkinter.Label(master=self.window, text="Brightness: {:d}".format(r))
            brightness_value_label.grid(row=0, column=0, sticky=tkinter.E)

            brightness_label = tkinter.Label(master=self.window, text="", bg=f'#{r:02x}{g:02x}{b:02x}',
                                             width=12, height=1)
            brightness_label.grid(row=0, column=1, columnspan=2, padx=5, pady=3)

        pos_label = tkinter.Label(master=self.window, text="Position: ({:d}, {:d}) ".format(self.x_pos, self.y_pos))
        pos_label.grid(row=1, column=0)

        self.frame_label = tkinter.Label(master=self.window, text="Frame: {:d} ".format(frame))
        self.frame_label.grid(row=1, column=1)

        self.time_label = tkinter.Label(master=self.window, text="Time: {:02d}:{:02d}:{:02d} "
                                        .format(time_hr, time_min, time_sec))
        self.time_label.grid(row=1, column=2)

        self.cali_button = tkinter.Button(master=self.window, text="Calibrate", command=self.calibrate_barcode_time)
        self.cali_button.grid(row=2, column=1)

        self.display_button = tkinter.Button(master=self.window, text="Display", command=self.display)
        self.display_button.grid(row=2, column=2)

    def calibrate_barcode_time(self):
        CalibrateBarcodeTimeWindow(self.barcode, self.time_label, self.frame_label, self.x_pos, self.y_pos)

    def display(self):
        if self.barcode.saved_frames is None:
            showerror("No Saved Frames", "This Barcode does not have\nthe saved frames to display.")
        else:
            DisplaySavedFramesWindow(barcode=self.barcode, mouse_x=self.x_pos, mouse_y=self.y_pos)

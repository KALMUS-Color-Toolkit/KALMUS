import tkinter

from kalmus.tkinter_windows.KALMUS_utils import resource_path


class CalibrateBarcodeTimeWindow():
    def __init__(self, barcode, time_label, frame_label, mouse_x, mouse_y):
        self.barcode = barcode
        self.time_label = time_label
        self.frame_label = frame_label
        self.x_pos = mouse_x
        self.y_pos = mouse_y

        self.window = tkinter.Tk()
        self.window.wm_title("At this point...")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        start_label = tkinter.Label(master=self.window, text="Start at (min:sec):")
        start_label.grid(row=0, column=0)

        self.start_entry = tkinter.Entry(self.window, textvariable="0", width=12)
        self.start_entry.grid(row=0, column=1, columnspan=1, padx=5, pady=1)

        end_label = tkinter.Label(master=self.window, text="End at (min:sec):")
        end_label.grid(row=1, column=0)

        self.end_entry = tkinter.Entry(self.window, textvariable="1", width=12)
        self.end_entry.grid(row=1, column=1, columnspan=1, padx=5, pady=1)

        fps_label = tkinter.Label(master=self.window, text="Frame per second (fps):")
        fps_label.grid(row=2, column=0)

        self.fps_entry = tkinter.Entry(self.window, textvariable="2", width=12)
        self.fps_entry.grid(row=2, column=1, columnspan=1, padx=5, pady=1)

        self.update_button = tkinter.Button(master=self.window, text="Update", command=self.update)
        self.update_button.grid(row=3, column=0, columnspan=2)

    def update(self):
        fps = self.fps_entry.get()
        if len(fps) != 0:
            self.barcode.fps = float(fps)

        start_str = str(self.start_entry.get())
        if len(start_str) != 0:
            split_pos = start_str.find(":")
            start_frame = int((int(start_str[:split_pos]) * 60 + int(start_str[split_pos + 1:])) * self.barcode.fps)
        else:
            start_frame = 0

        end_str = str(self.end_entry.get())
        if len(end_str) != 0:
            split_pos = end_str.find(":")
            total_frames = (int(end_str[:split_pos]) * 60 + int(end_str[split_pos + 1:])) * self.barcode.fps
            total_frames -= start_frame
            total_frames = int(total_frames)
        else:
            total_frames = self.barcode.get_barcode().shape[0] * self.barcode.get_barcode().shape[1] \
                           * self.barcode.sampled_frame_rate

        self.barcode.scale_factor = total_frames / (self.barcode.get_barcode().shape[0] *
                                                    self.barcode.get_barcode().shape[1] *
                                                    self.barcode.sampled_frame_rate)

        frame = (self.barcode.skip_over + self.barcode.sampled_frame_rate * \
                ((self.x_pos * self.barcode.get_barcode().shape[0]) + self.y_pos)) * self.barcode.scale_factor
        frame = int(frame)

        self.frame_label['text'] = "Frame: {:d} ".format(frame)

        time_tot_sec = frame / self.barcode.fps
        time_sec = int(time_tot_sec % 60)
        time_min = int((time_tot_sec / 60) % 60)
        time_hr = int(time_tot_sec / 3600)

        self.time_label['text'] = "Time: {:02d}:{:02d}:{:02d} ".format(time_hr, time_min, time_sec)

        self.window.destroy()

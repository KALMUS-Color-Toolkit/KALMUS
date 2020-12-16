import cv2
import tkinter
import copy


class GenerateBarcodeWindow():
    def __init__(self, barcode_generator, barcode_stack):
        self.barcode_generator = barcode_generator
        self.barcode_stack = barcode_stack
        self.window = tkinter.Tk()
        self.window.wm_title("Barcode generator")
        self.window.geometry("670x300")

        self.video = None

        # Extraction Type
        barcode_type_label = tkinter.Label(self.window, text="Barcode Type: ")
        barcode_type_label.grid(row=0, column=0)

        frame_type_label = tkinter.Label(self.window, text="Frame Type: ")
        frame_type_label.grid(row=1, column=0)

        color_metric_label = tkinter.Label(self.window, text="Color metric: ")
        color_metric_label.grid(row=2, column=0)

        self.barcode_type_var = tkinter.StringVar(self.window)
        self.barcode_type_var.set("Color")

        # Dropdown for extraction
        dropdown_bar_type = tkinter.OptionMenu(self.window, self.barcode_type_var, "Color", "Brightness")
        dropdown_bar_type.grid(row=0, column=1)

        self.frame_type_var = tkinter.StringVar(self.window)
        self.frame_type_var.set("Whole_frame")

        dropdown_frame_type = tkinter.OptionMenu(self.window, self.frame_type_var, "Whole_frame", "Low_contrast_region",
                                                 "High_contrast_region", "Foreground", "Background")
        dropdown_frame_type.grid(row=1, column=1)

        self.color_metric_var = tkinter.StringVar(self.window)
        self.color_metric_var.set("Average")

        dropdown_color_metric = tkinter.OptionMenu(self.window, self.color_metric_var, "Average", "Median", "Mode",
                                                   "Top-dominant", "Weighted-dominant", "Bright", "Brightest")
        dropdown_color_metric.grid(row=2, column=1)

        # Acquisition setup
        self.skip_over_label = tkinter.Label(self.window, text="Start at (frames): ")
        self.skip_over_label.grid(row=0, column=2)

        self.sampled_rate_label = tkinter.Label(self.window, text="Sampled every (frames): ")
        self.sampled_rate_label.grid(row=1, column=2)

        self.total_frames_label = tkinter.Label(self.window, text="Total frames: ")
        self.total_frames_label.grid(row=2, column=2)

        # Unit option
        self.acquisition_label = tkinter.Label(self.window, text="Acquistion unit")
        self.acquisition_label.grid(row=0, column=5)

        self.acquisition_option = tkinter.StringVar(self.window)
        self.acquisition_option.set("Frame")

        radio_frame = tkinter.Radiobutton(self.window, text="Frame", variable=self.acquisition_option,
                                          value="Frame", anchor='w',
                                          command=self.frame_unit)
        radio_frame.grid(row=1, column=5, sticky=tkinter.W)
        radio_frame.select()

        radio_time = tkinter.Radiobutton(self.window, text="Time", variable=self.acquisition_option,
                                         value="Time", anchor='w',
                                         command=self.time_unit)
        radio_time.grid(row=2, column=5, sticky=tkinter.W)
        # Input entry for acquisition setup
        self.skip_over_entry = tkinter.Entry(self.window, textvariable="0", width=12)
        self.skip_over_entry.grid(row=0, column=3, columnspan=2)

        self.sampled_rate_entry = tkinter.Entry(self.window, textvariable="1", width=12)
        self.sampled_rate_entry.grid(row=1, column=3, columnspan=2)

        self.total_frames_entry = tkinter.Entry(self.window, textvariable="1000", width=12)
        self.total_frames_entry.grid(row=2, column=3, columnspan=2)

        video_filename_label = tkinter.Label(self.window, text="Media filename: ")
        video_filename_label.grid(row=3, column=0, columnspan=1)

        self.video_filename_entry = tkinter.Entry(self.window, textvariable="", width=55)
        self.video_filename_entry.grid(row=3, column=1, columnspan=3)

        self.browse_folder_button = tkinter.Button(self.window, text='Browse', command=self.browse_folder)
        self.browse_folder_button.grid(row=3, column=4)

        # Letterbox options
        self.letterbox_option = tkinter.StringVar(self.window)
        self.letterbox_option.set("Auto")  # initialize

        letterbox_label = tkinter.Label(self.window, text="Remove Letterbox: ")
        letterbox_label.grid(row=4, column=0, columnspan=1)

        radio_auto = tkinter.Radiobutton(self.window, text="Auto", variable=self.letterbox_option,
                                         value="Auto", anchor='w',
                                         command=self.disable_setup)
        radio_auto.grid(row=5, column=0, sticky=tkinter.W)
        radio_auto.select()

        radio_manual = tkinter.Radiobutton(self.window, text="Manual", variable=self.letterbox_option,
                                           value="Manual", anchor='w',
                                           command=self.enable_setup)
        radio_manual.grid(row=6, column=0, sticky=tkinter.W)

        # Letterbox setup
        high_ver_label = tkinter.Label(self.window, text="Upper vertical: ")
        high_ver_label.grid(row=5, column=1, columnspan=1)

        low_ver_label = tkinter.Label(self.window, text="Lower vertical: ")
        low_ver_label.grid(row=6, column=1, columnspan=1)

        self.high_ver_entry = tkinter.Entry(self.window, textvariable="-1", width=4, state="disabled")
        self.high_ver_entry.grid(row=5, column=2, columnspan=1, sticky=tkinter.W)

        self.low_ver_entry = tkinter.Entry(self.window, textvariable="-2", width=4, state="disabled")
        self.low_ver_entry.grid(row=6, column=2, columnspan=1, sticky=tkinter.W)

        left_hor_label = tkinter.Label(self.window, text="Left horizontal: ")
        left_hor_label.grid(row=5, column=3, columnspan=1)

        right_hor_label = tkinter.Label(self.window, text="right horizontal: ")
        right_hor_label.grid(row=6, column=3, columnspan=1)

        self.left_hor_entry = tkinter.Entry(self.window, textvariable="-3", width=4, state="disabled")
        self.left_hor_entry.grid(row=5, column=4, columnspan=1)

        self.right_hor_entry = tkinter.Entry(self.window, textvariable="-4", width=4, state="disabled")
        self.right_hor_entry.grid(row=6, column=4, columnspan=1)

        self.generate_button = tkinter.Button(master=self.window, text="Generate Barcode",
                                              command=self.generate_barcode)
        self.generate_button.grid(row=7, column=2, sticky=tkinter.W)

        self.window.mainloop()

    def time_unit(self):
        self.skip_over_label['text'] = "Skip-over (mins:secs): "
        self.sampled_rate_label['text'] = "Sample every (secs): "
        self.total_frames_label['text'] = "End at (mins:secs): "

    def frame_unit(self):
        self.skip_over_label['text'] = "Start at (frames): "
        self.sampled_rate_label['text'] = "Sampled every (frames): "
        self.total_frames_label['text'] = "Total frames: "

    def browse_folder(self):
        filename = tkinter.filedialog.askopenfilename(initialdir="/", title="Select Media file",
                                                      filetypes=(("mp4 files", "*.mp4"), ("avi files", "*.avi"),
                                                                 ("m4v files", "*.m4v"), ("All files", "*.*")))
        self.video_filename_entry.delete(0, tkinter.END)
        self.video_filename_entry.insert(0, filename)

    def generate_barcode(self):
        barcode_type = self.barcode_type_var.get()
        frame_type = self.frame_type_var.get()
        color_metric = self.color_metric_var.get()

        unit_type = self.acquisition_option.get()
        video_filename = str(self.video_filename_entry.get())

        if unit_type == "Frame":
            skip_over = int(self.skip_over_entry.get())
            sampled_frame_rate = int(self.sampled_rate_entry.get())
            total_frames = int(self.total_frames_entry.get())
        elif unit_type == "Time":
            self.video = cv2.VideoCapture(video_filename)
            fps = self.video.get(cv2.CAP_PROP_FPS)

            skip_over_str = str(self.skip_over_entry.get())
            split_pos = skip_over_str.find(":")
            skip_over = int((int(skip_over_str[:split_pos]) * 60 + int(skip_over_str[split_pos + 1:])) * fps)

            sampled_frame_rate_str = str(self.sampled_rate_entry.get())
            sampled_frame_rate = int(float(sampled_frame_rate_str) * fps)

            total_frames_str = str(self.total_frames_entry.get())
            split_pos = total_frames_str.find(":")
            total_frames = (int(total_frames_str[:split_pos]) * 60 + int(total_frames_str[split_pos + 1:])) * fps
            total_frames -= skip_over
            total_frames = int(total_frames)

        self.barcode_generator.barcode_type = barcode_type
        self.barcode_generator.frame_type = frame_type
        self.barcode_generator.color_metric = color_metric
        self.barcode_generator.sampled_frame_rate = sampled_frame_rate
        self.barcode_generator.skip_over = skip_over
        self.barcode_generator.total_frames = total_frames

        self.generate_button["text"] = "Processing..."
        if self.letterbox_option.get() == "Manual":
            high_ver = int(self.high_ver_entry.get())
            low_ver = int(self.low_ver_entry.get())
            left_hor = int(self.left_hor_entry.get())
            right_hor = int(self.right_hor_entry.get())
            self.barcode_generator.generate_barcode(video_filename, user_defined_letterbox=True,
                                                    low_ver=low_ver, high_ver=high_ver,
                                                    left_hor=left_hor, right_hor=right_hor)
        elif self.letterbox_option.get() == "Auto":
            self.barcode_generator.generate_barcode(video_filename)

        start_pos = video_filename.rfind("/") + 1
        if start_pos < 0:
            start_pos = 0
        end_pos = video_filename.rfind(".")
        videoname = video_filename[start_pos:end_pos] + "_" + barcode_type + "_" + frame_type + "_" + color_metric \
                    + "_" + str(skip_over) + "_" + str(sampled_frame_rate) + "_" + str(total_frames)

        barcode = self.barcode_generator.get_barcode()
        barcode.video = None
        self.barcode_stack[videoname] = copy.deepcopy(barcode)

        self.window.destroy()

    def disable_setup(self):
        self.high_ver_entry.config(state="disabled")
        self.low_ver_entry.config(state="disabled")
        self.left_hor_entry.config(state="disabled")
        self.right_hor_entry.config(state="disabled")

    def enable_setup(self):
        self.high_ver_entry.config(state="normal")
        self.low_ver_entry.config(state="normal")
        self.left_hor_entry.config(state="normal")
        self.right_hor_entry.config(state="normal")

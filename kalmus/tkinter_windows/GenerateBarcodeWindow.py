""" GenerateBarcodeWindow Class """

import cv2
import tkinter
import tkinter.filedialog
from tkinter.messagebox import showerror, showwarning, showinfo
import copy
import os
import threading

from kalmus.tkinter_windows.meta_info_windows.SpecifyMetaDataWindow import SpecifyMetaDataWindow
from kalmus.tkinter_windows.gui_utils import resource_path


class GenerateBarcodeWindow():
    """
    GenerateBarcodeWindow Class
    GUI window for user to generate the barcode from a video file
    """

    def __init__(self, barcode_generator, barcode_stack):
        """
        Initialize

        :param barcode_generator: The barcode generator
        :param barcode_stack: The dictionary that stores all the barcode on the memory
        """
        self.barcode_generator = barcode_generator
        self.barcode_stack = barcode_stack

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Barcode Generator")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # A temporary meta data dictionary that will hold the meta information given by the user
        self.meta_data_dict = {}

        # video object capture by cv2
        self.video = None

        # Label prompt for the generated barcode's barcode type
        barcode_type_label = tkinter.Label(self.window, text="Barcode Type: ")
        barcode_type_label.grid(row=0, column=0)

        # Label prompt for the frame sampling type
        frame_type_label = tkinter.Label(self.window, text="Frame Type: ")
        frame_type_label.grid(row=1, column=0)

        # Label prompt for the color/brightness metric
        color_metric_label = tkinter.Label(self.window, text="Color metric: ")
        color_metric_label.grid(row=2, column=0)

        # Variable that stores the user's choice of generated barcode type
        self.barcode_type_var = tkinter.StringVar(self.window)
        self.barcode_type_var.set("Color")

        # Dropdown menu for the barcode type selection
        dropdown_bar_type = tkinter.OptionMenu(self.window, self.barcode_type_var, "Color", "Brightness")
        dropdown_bar_type.grid(row=0, column=1)

        # Variable that stores the user's choice of frame sampling type
        self.frame_type_var = tkinter.StringVar(self.window)
        self.frame_type_var.set("Whole_frame")

        # Dropdown menu for the frame sampling type selection
        dropdown_frame_type = tkinter.OptionMenu(self.window, self.frame_type_var, "Whole_frame", "Low_contrast_region",
                                                 "High_contrast_region", "Foreground", "Background")
        dropdown_frame_type.grid(row=1, column=1)

        # Variable that stores the user's choice of color metric
        self.color_metric_var = tkinter.StringVar(self.window)
        self.color_metric_var.set("Average")

        # Dropdown menu for the color metric selection
        dropdown_color_metric = tkinter.OptionMenu(self.window, self.color_metric_var, "Average", "Median", "Mode",
                                                   "Top-dominant", "Weighted-dominant", "Bright", "Brightest")
        dropdown_color_metric.grid(row=2, column=1)

        # Label prompt for the skip over specification
        self.skip_over_label = tkinter.Label(self.window, text="Start at (frames): ")
        self.skip_over_label.grid(row=0, column=2)

        # Label prompt for the sample rate specification
        self.sampled_rate_label = tkinter.Label(self.window, text="Sample every (frames): ")
        self.sampled_rate_label.grid(row=1, column=2)

        # Label prompt for the total frame included specification
        self.total_frames_label = tkinter.Label(self.window, text="Total frames: ")
        self.total_frames_label.grid(row=2, column=2)

        # Acquisition unit specification (in frames or in time)
        self.acquisition_label = tkinter.Label(self.window, text="Acquistion unit")
        self.acquisition_label.grid(row=0, column=5)

        # Variable that stores the user's choice of acquisition unit
        self.acquisition_option = tkinter.StringVar(self.window)
        self.acquisition_option.set("Frame")

        # Radio button for the Acquisition unit (Frame/Time) selection
        radio_frame = tkinter.Radiobutton(self.window, text="Frame", variable=self.acquisition_option,
                                          value="Frame", anchor='w',
                                          command=self.frame_unit)
        radio_frame.grid(row=1, column=5, sticky=tkinter.W)
        radio_frame.select()

        radio_time = tkinter.Radiobutton(self.window, text="Time", variable=self.acquisition_option,
                                         value="Time", anchor='w',
                                         command=self.time_unit)
        radio_time.grid(row=2, column=5, sticky=tkinter.W)

        # Text entry for the skip over specification
        self.skip_over_entry = tkinter.Entry(self.window, textvariable="0", width=12)
        self.skip_over_entry.grid(row=0, column=3, columnspan=2)

        # Text entry for the sampling rate specification
        self.sampled_rate_entry = tkinter.Entry(self.window, textvariable="1", width=12)
        self.sampled_rate_entry.grid(row=1, column=3, columnspan=2)

        # Text entry for the total frames specification
        self.total_frames_entry = tkinter.Entry(self.window, textvariable="1000", width=12)
        self.total_frames_entry.grid(row=2, column=3, columnspan=2)

        # Label prompt for the video file name input
        video_filename_label = tkinter.Label(self.window, text="Media file path: ")
        video_filename_label.grid(row=3, column=0, columnspan=1)

        # Text entry for the video file name specification
        self.video_filename_entry = tkinter.Entry(self.window, textvariable="", width=55)
        self.video_filename_entry.grid(row=3, column=1, columnspan=3)

        # Button to browse the folder
        self.browse_folder_button = tkinter.Button(self.window, text='Browse', command=self.browse_folder)
        self.browse_folder_button.grid(row=3, column=4)

        # Variable that stores the letter box option (automatic/user defined)
        self.letterbox_option = tkinter.StringVar(self.window)
        self.letterbox_option.set("Auto")  # initialize

        # Label prompt for the letter box remove option
        letterbox_label = tkinter.Label(self.window, text="Remove Letterbox: ")
        letterbox_label.grid(row=4, column=0, columnspan=1)

        # Radio button for the letter box remove option
        radio_auto = tkinter.Radiobutton(self.window, text="Auto", variable=self.letterbox_option,
                                         value="Auto", anchor='w',
                                         command=self.disable_setup)
        radio_auto.grid(row=5, column=0, sticky=tkinter.W)
        radio_auto.select()

        radio_manual = tkinter.Radiobutton(self.window, text="Manual", variable=self.letterbox_option,
                                           value="Manual", anchor='w',
                                           command=self.enable_setup)
        radio_manual.grid(row=6, column=0, sticky=tkinter.W)

        # User defined letter box label prompt
        high_ver_label = tkinter.Label(self.window, text="Upper vertical: ")
        high_ver_label.grid(row=5, column=1, columnspan=1)

        low_ver_label = tkinter.Label(self.window, text="Lower vertical: ")
        low_ver_label.grid(row=6, column=1, columnspan=1)

        # User defined letter box text entry
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

        # Variable that stores 0 for not saving frames during the generation 1 for saving frames during the generation
        self.var_saved_frame = tkinter.IntVar(self.window)

        # Checkbox for the user to choose whether save the frames or not during barcode generation
        self.checkbox_saved_frame = tkinter.Checkbutton(self.window, text="Save Frames  ",
                                                        variable=self.var_saved_frame,
                                                        onvalue=1, offvalue=0, command=self.update_save_frame_entry)
        self.checkbox_saved_frame.grid(row=7, column=0)

        # Label prompt for saving frame
        save_frame_label = tkinter.Label(master=self.window, text="Save every (secs):")
        save_frame_label.grid(row=7, column=1, sticky=tkinter.E)

        # Text entry for the saved frames rate specification
        self.save_frame_entry = tkinter.Entry(self.window, textvariable="-8", width=4, state="normal")
        self.save_frame_entry.grid(row=7, column=2, sticky=tkinter.W)
        self.save_frame_entry.delete(0, tkinter.END)
        self.save_frame_entry.insert(0, "4")
        self.save_frame_entry.config(state="disabled")

        # Variable that stores 0 for not saving frames during the generation 1 for rescaling frame
        # during the generation
        self.var_rescale_frame = tkinter.IntVar(self.window)

        # Checkbox for the user to choose whether to rescale the frames or not during the barcode generation
        self.checkbox_rescale_frame = tkinter.Checkbutton(self.window, text="Rescale Frames", width=12,
                                                          variable=self.var_rescale_frame,
                                                          onvalue=1, offvalue=0, command=self.update_rescale_entry)
        self.checkbox_rescale_frame.grid(row=7, column=3, sticky=tkinter.E)

        # Text entry for the rescale factor specification
        self.rescale_factor_entry = tkinter.Entry(self.window, textvariable="-7", width=4, state="normal")
        self.rescale_factor_entry.grid(row=7, column=4)
        self.rescale_factor_entry.delete(0, tkinter.END)
        self.rescale_factor_entry.insert(0, "0.5")
        self.rescale_factor_entry.config(state="disabled")

        # Variable that stores 0 for single thread generation 1 for multi-thread generation
        self.var_multi_thread = tkinter.IntVar(self.window)

        # Checkbox for the user to choose whether use the multi-thread or not for barcode generation
        self.checkbox_multi_thread = tkinter.Checkbutton(self.window, text="Multi-Thread:",
                                                         variable=self.var_multi_thread,
                                                         onvalue=1, offvalue=0, command=self.update_thread_entry)

        self.checkbox_multi_thread.grid(row=8, column=0)

        # Text entry for the thread specification
        self.thread_entry = tkinter.Entry(self.window, textvariable="-6", width=4, state="normal")
        self.thread_entry.grid(row=8, column=1, sticky=tkinter.W)
        self.thread_entry.delete(0, tkinter.END)
        self.thread_entry.insert(0, "4")
        self.thread_entry.config(state="disabled")

        # Button to generate the barcode
        self.generate_button = tkinter.Button(master=self.window, text="Generate Barcode",
                                              command=self.generate_barcode_thread)
        self.generate_button.grid(row=8, column=2, sticky=tkinter.W, rowspan=1, pady=5)

        # Button to specify the meta data of the generated barcode
        self.specify_data_button = tkinter.Button(master=self.window, text="Specify Meta Data",
                                                  command=self.specify_data)
        self.specify_data_button.grid(row=8, column=3, sticky=tkinter.W, rowspan=1, pady=5)

        self.window.protocol("WM_DELETE_WINDOW", self.quit)

        # Start the window
        self.window.mainloop()

    def quit(self):
        """
        Quit the main window
        """
        self.window.quit()
        self.window.destroy()

    def specify_data(self):
        """
        Instantiate the SpecifyMetaDataWindow
        """
        SpecifyMetaDataWindow(self.meta_data_dict)

    def update_thread_entry(self):
        """
        Enable or disable and change the label prompt when user check/uncheck the multi-thread checkbox
        """
        if self.var_multi_thread.get() == 0:
            self.checkbox_multi_thread["text"] = "Multi-Thread:"
            self.thread_entry.config(state="disabled")
        elif self.var_multi_thread.get() == 1:
            self.checkbox_multi_thread["text"] = "# of Threads:"
            self.thread_entry.config(state="normal")

    def update_rescale_entry(self):
        """
        Enable or disable and change the label prompt when user check/uncheck the rescale frames checkbox
        """
        if self.var_rescale_frame.get() == 0:
            self.checkbox_rescale_frame["text"] = "Rescale Frames"
            self.rescale_factor_entry.config(state="disabled")
        elif self.var_rescale_frame.get() == 1:
            self.checkbox_rescale_frame["text"] = "By a factor of: "
            self.rescale_factor_entry.config(state="normal")

    def update_save_frame_entry(self):
        """
        Enable or disable the text entry when user check/uncheck the save frames checkbox
        """
        if self.var_saved_frame.get() == 0:
            self.save_frame_entry.config(state="disabled")
        elif self.var_saved_frame.get() == 1:
            self.save_frame_entry.config(state="normal")

    def time_unit(self):
        """
        Change the acquisition unit to Time when user switch to the time radio button
        """
        self.skip_over_label['text'] = "Start at (mins:secs): "
        self.sampled_rate_label['text'] = "Sample every (secs): "
        self.total_frames_label['text'] = "End at (mins:secs): "

    def frame_unit(self):
        """
        Change the acquisition unit to Frame when user switch to the frame radio button
        """
        self.skip_over_label['text'] = "Start at (frames): "
        self.sampled_rate_label['text'] = "Sample every (frames): "
        self.total_frames_label['text'] = "Total frames: "

    def browse_folder(self):
        """
        Browse the folder
        """
        # Get the file name from the user specification
        filename = tkinter.filedialog.askopenfilename(initialdir=".", title="Select Media file",
                                                      filetypes=(("mp4 files", "*.mp4"), ("avi files", "*.avi"),
                                                                 ("m4v files", "*.m4v"), ("All files", "*.*")))

        # Update the file name to the text entry
        self.video_filename_entry.delete(0, tkinter.END)
        self.video_filename_entry.insert(0, filename)

    def generate_barcode_thread(self):
        """
        Generate the barcode in a another thread
        to avoid the frozen tkinter window issue

        :return:
        """
        threading.Thread(target=self.generate_barcode).start()

    def acquire_generation_param(self):
        """
        Acquire the barcode generation parameters
        """
        # Get barcode type, frame sampling type, and color/brightness metric
        barcode_type = self.barcode_type_var.get()
        frame_type = self.frame_type_var.get()
        color_metric = self.color_metric_var.get()

        # Get the acquisition unit
        unit_type = self.acquisition_option.get()

        # Get the file name/path of the input video
        video_filename = str(self.video_filename_entry.get())

        if not os.path.exists(video_filename):
            showerror("Video File Not Exists", "Video file not found!\nPlease check the file path.")
            raise FileNotFoundError()

        # Get the correct acquisition parameters based on the acqusition unit
        if unit_type == "Frame":
            skip_over_str = self.skip_over_entry.get()
            if len(skip_over_str) == 0 or skip_over_str.lower() == "start":
                skip_over = 0
            else:
                skip_over = int(self.skip_over_entry.get())

            total_frames_str = self.total_frames_entry.get()
            if len(total_frames_str) == 0 or total_frames_str.lower() == "end":
                total_frames = int(1e8)
            else:
                total_frames = int(self.total_frames_entry.get())

            sampled_frame_rate_str = self.sampled_rate_entry.get()
            if len(sampled_frame_rate_str) == 0:
                showwarning("Sample Frame not Specified", "Sample frame rate is not given.\n"
                                                          "Default sample rate 1 frame every input frame is used.")
                sampled_frame_rate = 1
            else:
                sampled_frame_rate = int(sampled_frame_rate_str)
        elif unit_type == "Time":
            self.video = cv2.VideoCapture(video_filename)
            fps = self.video.get(cv2.CAP_PROP_FPS)

            skip_over_str = str(self.skip_over_entry.get())
            if len(skip_over_str) == 0 or skip_over_str.lower() == "start":
                skip_over = 0
            else:
                split_pos = skip_over_str.find(":")
                skip_over = int((int(skip_over_str[:split_pos]) * 60 + int(skip_over_str[split_pos + 1:])) * fps)

            sampled_frame_rate_str = str(self.sampled_rate_entry.get())
            if len(sampled_frame_rate_str) == 0:
                showwarning("Sample Frame not Specified", "Sample frame rate is not given.\n"
                                                          "Default sample rate 1 frame every input frame is used.")
                sampled_frame_rate = 1
            else:
                sampled_frame_rate = int(round(float(sampled_frame_rate_str) * fps))

            total_frames_str = str(self.total_frames_entry.get())
            if len(total_frames_str) == 0 or total_frames_str.lower() == "end":
                total_frames = int(1e8)
            else:
                split_pos = total_frames_str.find(":")
                total_frames = (int(total_frames_str[:split_pos]) * 60 + int(total_frames_str[split_pos + 1:])) * fps
                total_frames -= skip_over
                total_frames = int(total_frames)
                total_frames //= sampled_frame_rate

        # Make sure the sampled frame rate >= 1 and the skip over >= 0 and total frame >= 0
        if sampled_frame_rate < 1:
            showwarning("Frame Sample Rate too Small", "The frame sample rate is too small.\n"
                                                       "It has been adjusted to the Minimum valid sample rate,\n"
                                                       "Sample 1 frame every frame (==use all frames)")
            sampled_frame_rate = 1
        if skip_over < 0:
            showwarning("Invalid Start time", "Invalid start time for the barcode generation.\n"
                                              "Start frames/time has been set to 0/00:00 (== start of film)")
            skip_over = 0
        if total_frames < 0:
            showwarning("Invalid Total Frames", "Invalid total frames\n"
                                                "or Barcode starts after it ends.\n"
                                                "Total frames has been adjusted to 0.")
            total_frames = 0

        return barcode_type, frame_type, color_metric, sampled_frame_rate, skip_over, total_frames, video_filename

    def generate_barcode(self):
        """
        Generate the barcode using the given parameters
        """
        self.disable_generate_button()
        try:
            barcode_type, frame_type, color_metric, sampled_frame_rate, skip_over, total_frames, video_filename = \
                self.acquire_generation_param()
        except FileNotFoundError:
            self.enable_generate_button()
            return
        except:
            showerror("Acquisition Parameters", "An unknown Error occurred when reading\n"
                                                "the acquisition parameters.\n\n"
                                                "Please make sure all parameters are positive\n"
                                                "Frames units must all be integers\n"
                                                "In Time unit, mins:secs in Start and End at must be integers\n"
                                                "Sample every (secs) can be decimals but not fraction.")
            self.enable_generate_button()
            return

        # Update all the parameters to the barcode generator
        self.barcode_generator.barcode_type = barcode_type
        self.barcode_generator.frame_type = frame_type
        self.barcode_generator.color_metric = color_metric
        self.barcode_generator.sampled_frame_rate = sampled_frame_rate
        self.barcode_generator.skip_over = skip_over
        self.barcode_generator.total_frames = total_frames

        # Check if user choose the multi-thread or not
        if self.var_multi_thread.get() == 0:
            multi_thread = None
        elif self.var_multi_thread.get() == 1:
            # If user choose to use the multi-thread, then get the number of threads that will be used
            try:
                multi_thread = int(self.thread_entry.get())
                if multi_thread < 1:
                    showwarning("Non Positive Thread Number", "Number of threads has been adjusted to 1.\n"
                                                              "Degenerated to single thread generation.")
                    multi_thread = 1
            except:
                showerror("Invalid Thread Number", "Invalid number of threads.\n"
                                                   "Number of threads must be an integer")
                self.enable_generate_button()
                return

        # Check if user choose to save the frames or not
        if self.var_saved_frame.get() == 1:
            save_frames = True
            try:
                save_frames_rate = int(self.save_frame_entry.get())
            except:
                showerror("Invalid Save Frame Rate", "Invalid Save frame rate.\n"
                                                     "Save frame rate must be a positive Integer.")
                self.enable_generate_button()
        else:
            save_frames_rate = -1
            save_frames = False

        # Check if user choose to rescale the frames or not
        if self.var_rescale_frame.get() == 1:
            try:
                rescale_factor = float(self.rescale_factor_entry.get())
            except:
                showerror("Invalid Rescale Factor", "Invalid frame rescale factor.\n"
                                                    "Must be a positive number.\n"
                                                    "It can be a decimal number but not fractions")
                self.enable_generate_button()
                return
        else:
            rescale_factor = -1

        # Check if user choose to define the letter box region manually
        if self.letterbox_option.get() == "Manual":
            try:
                # Update the letter box parameters, if user choose Manual
                high_ver = int(self.high_ver_entry.get())
                low_ver = int(self.low_ver_entry.get())
                left_hor = int(self.left_hor_entry.get())
                right_hor = int(self.right_hor_entry.get())
                # Start the generation
                self.barcode_generator.generate_barcode(video_filename, user_defined_letterbox=True,
                                                        low_ver=low_ver, high_ver=high_ver,
                                                        left_hor=left_hor, right_hor=right_hor,
                                                        num_thread=multi_thread, save_frames=save_frames,
                                                        rescale_frames_factor=rescale_factor,
                                                        save_frames_rate=save_frames_rate)
            except:
                showwarning("Error Occurred in Barcode Generation", "An unknown Error occurred in the barcode "
                                                                    "generation.\nPlease check the letterbox set up"
                                                                    " and the other parameters' specification.")
                self.enable_generate_button()
                return
        elif self.letterbox_option.get() == "Auto":
            # try:
                # If not, start the generation.
                # The letter box will be automatically found during the generation process
            self.barcode_generator.generate_barcode(video_filename, num_thread=multi_thread,
                                                    save_frames=save_frames,
                                                    rescale_frames_factor=rescale_factor,
                                                    save_frames_rate=save_frames_rate)
            # except:
            #     showwarning("Error Occurred in Barcode Generation", "An unknown Error occurred in the barcode "
            #                                                         "generation.\nPlease check the parameters' "
            #                                                         "specification.")
            #     self.enable_generate_button()
            #     return

        # Correct the total frames
        total_frames = self.barcode_generator.get_barcode().total_frames

        # Get the key of the barcode, which will be later stored in the memory stack (dictionary)
        start_pos = video_filename.rfind("/") + 1
        if start_pos < 0:
            start_pos = 0
        end_pos = video_filename.rfind(".")
        videoname = video_filename[start_pos:end_pos] + "_" + barcode_type + "_" + frame_type + "_" + color_metric \
                    + "_" + str(skip_over) + "_" + str(sampled_frame_rate) + "_" + str(total_frames)

        # Get the barcode from the barcode generator
        barcode = self.barcode_generator.get_barcode()

        # Clear the cv2 captured video object
        barcode.video = None

        # Update the user pre-defined meta data to the computed barcode
        barcode.meta_data = copy.deepcopy(self.meta_data_dict)

        # Add the generated barcode to the memory stack (dictionary)
        self.barcode_stack[videoname] = copy.deepcopy(barcode)

        # Enable the generate button for the next barcode generation request
        self.enable_generate_button()

        # Reset the meta data to the initial state
        self.meta_data_dict = {}

        # Show barcode generation success message
        showinfo("Finished Successfully", "{:s} {:s} {:s} Barcode of the input video:\n"
                                          "{:20s}\n"
                                          "has been successfully generated!\n\n"
                                          "Barcode is saved in the memory with name: {:20s}".format(color_metric,
                                                                                                    frame_type,
                                                                                                    barcode_type,
                                                                                                    video_filename,
                                                                                                    videoname))

    def disable_generate_button(self):
        """
        Disable the generate button and Specify Meta Data button once generation starts
        """
        # Update the generate button text to the processing
        self.generate_button["text"] = "  Processing... "
        self.generate_button.config(state="disabled")
        self.specify_data_button.config(state="disabled")

    def enable_generate_button(self):
        """
        Enable the generate button and Specify Meta Data button in case of failed generation
        """
        # Change the button text back to Generate Barcode
        self.generate_button["text"] = "Generate Barcode"
        self.generate_button.config(state="normal")
        self.specify_data_button.config(state="normal")

    def disable_setup(self):
        """
        Disable the letter box setup entry if user choose the Auto radio button
        """
        self.high_ver_entry.config(state="disabled")
        self.low_ver_entry.config(state="disabled")
        self.left_hor_entry.config(state="disabled")
        self.right_hor_entry.config(state="disabled")

    def enable_setup(self):
        """
        Enable the letter box setup entry if user choose the Manual radio button
        """
        self.high_ver_entry.config(state="normal")
        self.low_ver_entry.config(state="normal")
        self.left_hor_entry.config(state="normal")
        self.right_hor_entry.config(state="normal")

""" MetaInfoWindow Class """

import tkinter
from kalmus.tkinter_windows.meta_info_windows.SpecifyMetaDataWindow import SpecifyMetaDataWindow
from kalmus.tkinter_windows.gui_utils import resource_path

keys = ["Film Title", "Directors", "Country of Origin", "Produced Year", "Genre"]


class MetaInfoWindow():
    """
    MetaInfoWindow Class
    GUI window that displays the meta information of the selected barcode
    """
    def __init__(self, barcode, barcodes_stack):
        """
        Initialize

        :param barcode: The barcode to check with the meta information
        :param barcodes_stack: The dictionary that store all the barcodes on the memory
        """
        self.barcode = barcode
        self.barcodes_stack = barcodes_stack

        # Initialize the window
        self.window = tkinter.Tk()
        self.window.wm_title("Barcode Meta Information")
        self.window.iconbitmap(resource_path("kalmus_icon.ico"))

        # Label prompt for the meta information display
        self.meta_info_label = tkinter.Label(self.window, text="", width=35, bg='white', anchor='w',
                                             justify=tkinter.LEFT)
        self.meta_info_label.grid(row=0, column=0, columnspan=2, sticky=tkinter.W)

        # Update the Meta information text
        self.refresh_text()

        # Button to refresh the displayed meta information of the barcode
        self.refresh_button = tkinter.Button(master=self.window, text="Refresh",
                                             command=self.refresh_text)
        self.refresh_button.grid(row=1, column=0)

        # Button to add/update meta information to the barcode
        self.add_info_button = tkinter.Button(master=self.window, text="Update Meta Info",
                                              command=self.update_meta_info)
        self.add_info_button.grid(row=1, column=1)

    def refresh_text(self):
        """
        Refresh the meta information text displayed for the barcode
        """
        meta_text = "Meta Information of the Barcode:\n"

        # Build the text using the keys and their values stored in the barcodes's meta information dictionary
        if self.barcode.meta_data is not None:
            for key in keys:
                if key in self.barcode.meta_data.keys():
                    format_string = "{: <s}   {:s}\n".format(str(key) + ":", str(self.barcode.meta_data[key]))
                    meta_text += format_string

        film_length, start_time, end_time = self.get_time_str()
        fps = self.barcode.fps
        meta_text += "\n{: <s}   {:s}\n{: <s}  {:s}\n{: <s}  {:s}\n\n{: <s}  {:.1f}"\
            .format("Film Length:", film_length,
                    "Barcode starts at", start_time,
                    "Barcode ends at", end_time,
                    "Frame rate (FPS):", fps)
        self.meta_info_label["text"] = meta_text

    def get_time_str(self):
        """
        Get string for film length in hrs:mins:secs, clip start time in hrs:mins:secs,
        and clip end time in hrs:mins:secs

        :return: Text string for film length, clip start time at film, clip end time at film
        """
        if self.barcode.fps is None:
            self.barcode.fps = 30

        film_length_in_secs = round(self.barcode.film_length_in_frames / self.barcode.fps)

        hrs, mins, secs = self.get_hr_min_sec_from_tot_sec(film_length_in_secs)
        film_length_str = "{:02d}:{:02d}:{:02d}".format(hrs, mins, secs)

        barcode_clip_length_secs = round(self.barcode.total_frames
                                         * (self.barcode.sampled_frame_rate / self.barcode.fps))
        clip_start_time_secs = round(self.barcode.skip_over / self.barcode.fps)

        hrs, mins, secs = self.get_hr_min_sec_from_tot_sec(clip_start_time_secs)
        clip_start_time_str = "{:02d}:{:02d}:{:02d}".format(hrs, mins, secs)

        clip_end_time_secs = clip_start_time_secs + barcode_clip_length_secs
        hrs, mins, secs = self.get_hr_min_sec_from_tot_sec(clip_end_time_secs)
        clip_end_time_str = "{:02d}:{:02d}:{:02d}".format(hrs, mins, secs)

        return film_length_str, clip_start_time_str, clip_end_time_str

    def get_hr_min_sec_from_tot_sec(self, tot_seconds):
        """
        Get the equivalent Hours:Minutes:Seconds representation from a given total seconds

        :param tot_seconds: Total seconds
        :return: Converted hours, minutes, and seconds representation Hours:Minutes:Seconds \
                 Hours >= 0, 60 > Minutes >= 0, 60 > Seconds >= 0
        """
        secs = tot_seconds % 60
        mins = int(tot_seconds / 60) % 60
        hrs = int(tot_seconds / 3600) % 60
        return hrs, mins, secs

    def update_meta_info(self):
        """
        Instantiate the SpecifyMetaDataWindow, if the user press the add info button
        """
        SpecifyMetaDataWindow(self.barcode.__dict__["meta_data"], barcode=self.barcode,
                              barcode_stacks=self.barcodes_stack)

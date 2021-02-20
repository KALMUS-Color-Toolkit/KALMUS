""" Barcode Generator Class"""

import numpy as np
import json

from kalmus.barcodes.Barcode import ColorBarcode, BrightnessBarcode

# Available metrics for computing the color of a frame
color_metrics = ["Average", "Median", "Mode", "Top-dominant", "Weighted-dominant",
                 "Brightest", "Bright"]

# Available types of sampling frame (which part of frame is region of interest)
frame_types = ["Whole_frame", "High_contrast_region", "Low_contrast_region", "Foreground", "Background"]

# Available types of barcode
barcode_types = ["Color", "Brightness"]


def build_barcode_from_json(path_to_json, barcode_type="Color"):
    """
    Helper function that build a barcode object from the attributes stored in a json file
    :param path_to_json: Path to the json file
    :param barcode_type: Type of the barcode that stored in the json file
    :return:
    """
    assert barcode_type in barcode_types, "Invalid barcode type. The available types of " \
                                          "the barcode are {:s}".format(str(barcode_types))
    with open(path_to_json, "r") as infile:
        object_dict = json.load(infile)
    infile.close()

    if barcode_type == "Color":
        barcode = ColorBarcode(color_metric=object_dict["color_metric"], frame_type=object_dict["frame_type"],
                               sampled_frame_rate=object_dict["sampled_frame_rate"],
                               skip_over=object_dict["skip_over"], total_frames=int(object_dict["total_frames"]),
                               barcode_type=barcode_type)

        barcode.colors = np.array(object_dict["colors"]).astype("uint8")

    elif barcode_type == "Brightness":
        barcode = BrightnessBarcode(color_metric=object_dict["color_metric"], frame_type=object_dict["frame_type"],
                                    sampled_frame_rate=object_dict["sampled_frame_rate"],
                                    skip_over=object_dict["skip_over"], total_frames=int(object_dict["total_frames"]),
                                    barcode_type=barcode_type)

        barcode.brightness = np.array(object_dict["brightness"]).astype("uint8")

    barcode.set_letterbox_bound(object_dict["low_bound_ver"], object_dict["high_bound_ver"],
                                object_dict["low_bound_hor"], object_dict["high_bound_hor"])

    if "meta_data" in object_dict.keys():
        barcode.meta_data = object_dict["meta_data"]

    barcode.barcode = np.array(object_dict["barcode"])

    barcode.video = None

    barcode.film_length_in_frames = int(object_dict["film_length_in_frames"])

    if "save_frames_in_generation" in object_dict.keys():
        if object_dict["save_frames_in_generation"]:
            barcode.save_frames_in_generationa = object_dict["save_frames_in_generation"]
            barcode.saved_frames = np.array(object_dict["saved_frames"])

    return barcode


class BarcodeGenerator():
    """
    Barcode Generator Class
    """
    def __init__(self, frame_type="Whole_frame", color_metric="Average", barcode_type="Color",
                 sampled_frame_rate=1, skip_over=0, total_frames=10):
        """
        Initialize the parameters for the barcode generator
        :param frame_type: The type of the frame sampling
        :param color_metric: The metric of computing the frame color
        :param barcode_type: The type of the generated barcode
        :param sampled_frame_rate: The frame sample rate
               (one frame will be sampled from every sampled_frame_rate frames)
        :param skip_over: How many frames to skip with at the beginning of the input video
        :param total_frames: Total number of frames that will be computed (included in the barcode/sampled frames)
        """
        assert frame_type in frame_types, "Invalid frame acquisition method. Five types of frame acquisition" \
                                          " methods are available including {:s}".format(str(frame_types))
        assert color_metric in color_metrics, "Invalid color metric. Seven color metrics are available " \
                                              "including {:s}".format(str(color_metrics))
        assert barcode_type in barcode_types, "Invalid barcode type. Two types of barcode are available " \
                                              "including {:s}".format(str(barcode_types))
        assert not (color_metric == "Bright" and frame_type in frame_types[1:]), \
            "Color metric Bright can not be used when the frame acquisition " \
            "methods are {:s}".format(str(frame_types[1:]))

        self.frame_type = frame_type
        self.color_metric = color_metric
        self.barcode_type = barcode_type
        self.sampled_frame_rate = sampled_frame_rate
        self.skip_over = skip_over
        self.total_frames = total_frames
        self.barcode = None

    def instantiate_barcode(self):
        """
        Instantiate the barcode object using the given generation parameters
        :return:
        """
        if self.barcode_type == "Color":
            self.barcode = ColorBarcode(self.color_metric, self.frame_type, self.sampled_frame_rate,
                                        self.skip_over, self.total_frames, barcode_type="Color")
        elif self.barcode_type == "Brightness":
            self.barcode = BrightnessBarcode(self.color_metric, self.frame_type, self.sampled_frame_rate,
                                             self.skip_over, self.total_frames, barcode_type="Brightness")

    def generate_barcode(self, video_file_path, user_defined_letterbox=False,
                         low_ver=-1, high_ver=-1, left_hor=-1, right_hor=-1,
                         num_thread=None, save_frames=False, rescale_frames_factor=-1,
                         save_frames_rate=4):
        """
        Generate the barcode
        :param video_file_path: The path to the video file
        :param user_defined_letterbox: Whether use the user defined the letterbox, or use the
                                       automatically found letterbox
        :param low_ver: The lower vertical letterbox given by user
        :param high_ver: The higher vertical letterbox given by user
        :param left_hor: The left horizontal letterbox given by user
        :param right_hor: The right horizontal letterbox given by user
        :param num_thread: Number of thread for computation. None == Single thread. num_thread > 1: multi-thread
        :param save_frames: Whether to save the frames during the barcode generation
        :param rescale_frames_factor: factor to rescale the input frames during the generation
        :return:
        """
        self.instantiate_barcode()
        if user_defined_letterbox:
            self.barcode.set_letterbox_bound(up_vertical_bound=high_ver, down_vertical_bound=low_ver,
                                             left_horizontal_bound=left_hor, right_horizontal_bound=right_hor)
        if save_frames and save_frames_rate > 0:
            self.barcode.enable_save_frames(sampled_rate=save_frames_rate)

        if rescale_frames_factor > 0:
            self.barcode.enable_rescale_frames_in_generation(rescale_frames_factor)

        if self.barcode_type == "Color":
            if num_thread is not None:
                self.barcode.multi_thread_collect_colors(video_file_path, num_thread)
            else:
                self.barcode.collect_colors(video_file_path)
        elif self.barcode_type == "Brightness":
            if num_thread is not None:
                self.barcode.multi_thread_collect_brightness(video_file_path, num_thread)
            else:
                self.barcode.collect_brightness(video_file_path)

    def generate_barcode_from_json(self, json_file_path, barcode_type=None):
        """
        Generate the barcode from a json file, which contain a dictionary representation of barcode object
        :param json_file_path: the path to the json file
        :param barcode_type: the type of the barcode saved in the json file
        :return:
        """
        if barcode_type is None:
            barcode_type = self.barcode_type
        self.barcode = build_barcode_from_json(json_file_path, barcode_type=barcode_type)

    def get_barcode(self):
        """
        return the barcode object stored in the Barcode generator
        :return:
        """
        return self.barcode

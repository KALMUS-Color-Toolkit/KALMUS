"""
Barcode Classes
"""

import copy
import json

import cv2
import numpy as np
import threading

from kalmus.utils import artist as artist
from kalmus.utils.artist import get_letter_box_from_frames, get_contrast_matrix_and_labeled_image

# Available metrics for computing the color of a frame
color_metrics = ["Average", "Median", "Mode", "Top-dominant", "Weighted-dominant",
                 "Brightest", "Bright"]


def foreback_segmentation(frame):
    """
    Helper function
    Segmented the input frame into two parts: foreground and background, using the GrabCut

    :param frame: Input frame
    :type frame: numpy.ndarray
    :return: 1D image of the foreground part of the image, and 1D image of the background part of the image \
             Expected shape== Number of pixels x channels
    :rtype: (numpy.ndarray, numpy.ndarray)
    """
    fore_frame, back_frame = artist.grabcut_foreback_segmentation(frame, start_row=0, row_size=frame.shape[0] - 1,
                                                                  start_col=frame.shape[1] // 6,
                                                                  col_size=frame.shape[1] * 2 // 3)
    return fore_frame, back_frame


class Barcode:
    """
    Barcode Class. Base class for ColorBarcode and BrightnessBarcode

    :param color_metric: The metric for computing the color of the frame
    :type color_metric: str
    :param frame_type: The type of frame sampling
    :type frame_type: str
    :param sampled_frame_rate: Frame sample rate: the frame sampled from every sampled_frame_rate.
    :type sampled_frame_rate: int
    :param skip_over: The number of frames to skip with at the beginning of the video
    :type skip_over: int
    :param total_frames: The total number of frames (computed) included in the barcode
    :type total_frames: int
    :param barcode_type: The type of the barcode
    :type barcode_type: str
    """

    def __init__(self, color_metric, frame_type, sampled_frame_rate=1, skip_over=0, total_frames=10,
                 barcode_type=None):
        """
        Initialize the barcode with the given parameters
        """
        self.color_metric = color_metric
        self.frame_type = frame_type
        self.barcode_type = barcode_type
        self.meta_data = {}

        self.sampled_frame_rate = sampled_frame_rate
        self.skip_over = skip_over
        self.total_frames = total_frames

        self.video = None
        self.film_length_in_frames = 0

        self.fps = None
        self.scale_factor = 1

        self.user_defined_letterbox = False
        self.low_bound_ver = 0
        self.high_bound_ver = 0
        self.low_bound_hor = 0
        self.high_bound_hor = 0

        self.barcode = None

        self.save_frames_in_generation = False
        self.saved_frames = None
        self.saved_frames_sampled_rate = -1
        self.saved_frame_height = 0

        self.rescale_frames_in_generation = False
        self.rescale_frame_factor = -1

    def read_video(self, video_path_name):
        """
        Read in the video from the given path

        :param video_path_name: The path to the video file
        :type video_path_name: str
        """
        self.video = cv2.VideoCapture(video_path_name)

        # Get the fps of the video
        self.fps = self.video.get(cv2.CAP_PROP_FPS)

        # Get the length of the video
        self.film_length_in_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.total_frames + self.skip_over > self.film_length_in_frames:
            self.total_frames = self.film_length_in_frames - self.skip_over

        # Find the letter box
        if not self.user_defined_letterbox:
            self.find_film_letterbox()

        if self.save_frames_in_generation:
            self._determine_save_frame_param()

    def find_film_letterbox(self, num_sample=30):
        """
        Automatically find the letter box bounds of the film.
        Function run the get_letter_box_from_frames helper function by num_sample times and take the median of bounds

        :param num_sample: Number of times running the get_letter_box_from_frames
        :type num_sample: int
        """
        possible_indexes = np.arange(self.film_length_in_frames // 6, self.film_length_in_frames * 5 // 6, 1)
        frame_indexes = np.random.choice(possible_indexes, num_sample, replace=True)

        possible_low_bound_ver = []
        possible_high_bound_ver = []
        possible_low_bound_hor = []
        possible_high_bound_hor = []

        for frame_index in frame_indexes:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = self.video.read()
            if success:
                low_bound_v, high_bound_v, low_bound_h, high_bound_h = get_letter_box_from_frames(frame)
                possible_low_bound_ver.append(low_bound_v)
                possible_high_bound_ver.append(high_bound_v)
                possible_low_bound_hor.append(low_bound_h)
                possible_high_bound_hor.append(high_bound_h)

        self.low_bound_ver = int(np.median(possible_low_bound_ver))
        self.high_bound_ver = int(np.median(possible_high_bound_ver))
        self.low_bound_hor = int(np.median(possible_low_bound_hor))
        self.high_bound_hor = int(np.median(possible_high_bound_hor))

    def remove_letter_box_from_frame(self, frame):
        """
        Remove the letter box from the frame using the known letter box bounds

        :param frame: Input original frame with letter box
        :type frame: numpy.ndarray
        :return: Cropped frame without letter box
        :rtype: numpy.ndarray
        """
        frame = frame[self.low_bound_ver: self.high_bound_ver, self.low_bound_hor: self.high_bound_hor, ...]
        return frame

    def process_frame(self, frame):
        """
        Process the original frame by cropping out the letter box and resample frame using the given frame type

        :param frame: Input orignal frame
        :type frame: numpy.ndarray
        :return: The processed and sampled frame
        :rtype: numpy.ndarray
        """
        frame = self.remove_letter_box_from_frame(frame)
        if self.rescale_frames_in_generation:
            frame = self._resize_frame(frame)

        if self.frame_type == "Whole_frame":
            processed_frame = frame
        elif self.frame_type == "High_contrast_region":
            contrast_matrix, labels = get_contrast_matrix_and_labeled_image(frame)
            highest_contrast_region = np.sum(contrast_matrix, axis=1).argmax()
            processed_frame = frame[labels == (highest_contrast_region + 1)]
        elif self.frame_type == "Low_contrast_region":
            contrast_matrix, labels = get_contrast_matrix_and_labeled_image(frame)
            lowest_contrast_region = np.sum(contrast_matrix, axis=1).argmin()
            processed_frame = frame[labels == (lowest_contrast_region + 1)]
        elif self.frame_type == "Foreground":
            fore_frame, _ = foreback_segmentation(frame)
            if fore_frame.size == 0:
                # Empty foreground part use the whole frame instead
                fore_frame = frame
            processed_frame = fore_frame
        elif self.frame_type == "Background":
            _, back_frame = foreback_segmentation(frame)
            if back_frame.size == 0:
                # Empty background part use the whole frame instead
                back_frame = frame
            processed_frame = back_frame

        return processed_frame

    def _resize_frame(self, frame):
        """
        resize the input frame with a factor of self.rescale_frame_factor

        :param frame: Input frame
        :type frame: numpy.ndarray
        :return: resized frame
        :rtype: numpy.ndarray
        """
        frame = cv2.resize(frame, dsize=(0, 0), fx=self.rescale_frame_factor, fy=self.rescale_frame_factor,
                           interpolation=cv2.INTER_NEAREST)
        return frame

    def get_color_from_frame(self, frame):
        """
        Compute the color of the input frame using the known color metric

        :param frame: Input frame
        :type frame: numpy.ndarray
        :return: The color of the frame computed using the known color metric
        :rtype: numpy.ndarray
        """
        if self.color_metric == "Average":
            color = artist.compute_mean_color(frame)
        elif self.color_metric == "Median":
            color = artist.compute_median_color(frame)
        elif self.color_metric == "Mode":
            color, count = artist.compute_mode_color(frame)
        elif self.color_metric == "Top-dominant":
            colors, dominances = artist.compute_dominant_color(frame, n_clusters=3)
            pos = np.argsort(dominances)[-1]
            color = colors[pos]
        elif self.color_metric == "Weighted-dominant":
            colors, dominances = artist.compute_dominant_color(frame, n_clusters=3)
            color = np.sum(colors * dominances.reshape(dominances.shape[0], 1), axis=0)
        elif self.color_metric == "Brightest":
            grey_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            pos = np.argwhere(grey_frame == grey_frame.max())[0]
            color = frame[pos[0], pos[1]].copy().astype("uint8")
        elif self.color_metric == "Bright":
            labels, bright_locations, dominance = artist.find_bright_spots(frame, n_clusters=3, return_all_pos=True)
            top_bright = np.argsort(dominance)[-1]
            top_bright_pos = (labels == top_bright)[:, 0]
            pos = bright_locations[top_bright_pos]
            frame = frame[pos[:, 0], pos[:, 1]].reshape(pos.shape[0], 1, 3)
            color = artist.compute_mean_color(frame)

        return color

    def get_barcode(self):
        """
        Return the barcode. If not exist reshape the stored computed colors/brightness first to get the barcode

        :return: Return the barcode
        :rtype: class:`kalmus.barcodes.Barcode.Barcode`
        """
        if self.barcode is None:
            self.reshape_barcode()
        return self.barcode

    def set_letterbox_bound(self, up_vertical_bound, down_vertical_bound,
                            left_horizontal_bound, right_horizontal_bound):
        """
        Manually set up the letter box bound of the film

        :param up_vertical_bound: The lower vertical bound
        :type up_vertical_bound: int
        :param down_vertical_bound: The higher vertical bound
        :type down_vertical_bound: int
        :param left_horizontal_bound: The left vertical bound
        :type left_horizontal_bound: int
        :param right_horizontal_bound: The right vertical bound
        :type right_horizontal_bound: int
        """
        self.enable_user_defined_letterbox()
        self.low_bound_ver = up_vertical_bound
        self.high_bound_ver = down_vertical_bound
        self.low_bound_hor = left_horizontal_bound
        self.high_bound_hor = right_horizontal_bound

    def enable_user_defined_letterbox(self):
        """
        Use the user defined letter box
        """
        self.user_defined_letterbox = True

    def automatic_find_letterbox(self):
        """
        Automatically find the letter box
        """
        self.find_film_letterbox()

    def enable_rescale_frames_in_generation(self, rescale_factor=1):
        """
        Rescale frames with a factor of rescale_factor for all frames processed in barcode generation

        :param rescale_factor: rescale factor
        :type rescale_factor: float
        """
        assert rescale_factor > 0, "Rescale factor must be Positive"
        self.rescale_frames_in_generation = True
        self.rescale_frame_factor = np.sqrt(rescale_factor)

    def add_meta_data(self, key, value):
        """
        Add the meta information that describes the barcode

        :param key: The key for the meta information
        :type key: str
        :param value: The value stored in that key
        :type value: str
        """
        assert key is not None, "The key for the adding data cannot be None"
        if self.meta_data is None:
            self.meta_data = {}
        self.meta_data[key] = value

    def enable_save_frames(self, sampled_rate=4):
        """
        Set the save frame in the generation of barcode to be True.
        This attribute, saved_frames_in_generation, should only be modified before the generation of barcode.
        Once the barcode is generated, this attribute should not be changed.

        :param sampled_rate: Save 1 frame every sampled_rate seconds
        :type sampled_rate: float
        """
        self.save_frames_in_generation = True
        self.saved_frames = []

        self.saved_frames_sampled_rate = sampled_rate

    def _determine_save_frame_param(self):
        """
        Private method
        Determine the parameters of saving frame during the generation process.
        At most 900 Frames will be saved for each barcode
        Save frame rate is, by default, saving one frame every 4 seconds
        Frame will resized to the width of 100 pixels with the same aspect ratio
        """
        assert self.video is not None, "Video must be read before determining the save frame rate"
        assert self.fps is not None, "FPS must be determined before determining the save frame rate"
        self.saved_frames_sampled_rate = round(self.fps * self.saved_frames_sampled_rate / self.sampled_frame_rate)
        sampled_rate_upper_bound = round(self.total_frames / (self.sampled_frame_rate * 900))
        if self.saved_frames_sampled_rate < sampled_rate_upper_bound:
            self.saved_frames_sampled_rate = sampled_rate_upper_bound

        # If the barcode is too short
        if self.saved_frames_sampled_rate <= 0:
            self.saved_frames_sampled_rate = 1

        height = self.high_bound_ver - self.low_bound_ver
        width = self.high_bound_hor - self.low_bound_hor

        aspect_ratio = height / width
        self.saved_frame_height = int(100 * aspect_ratio)

    def save_frames(self, cur_used_frame, frame, frame_arr=None):
        """
        Private method
        Save the frame during the generation process.
        This functions should only be invoked during the generation process.

        :param cur_used_frame: How many frames have been read in
        :type cur_used_frame: int
        :param frame: Current frame (original unprocessed frame)
        :type frame: numpy.ndarray
        :param frame_arr: Array that stored the saved frames
        :type frame_arr: list
        """
        if cur_used_frame % self.saved_frames_sampled_rate == 0:
            frame = self.remove_letter_box_from_frame(frame)
            resized_frame = cv2.resize(frame, dsize=(100, self.saved_frame_height))
            if frame_arr is not None:
                frame_arr.append(resized_frame)
            else:
                self.saved_frames.append(resized_frame)

    def save_as_json(self, filename=None):
        """
        Save the barcode into the json file

        :param filename: The name of the saved json file
        :type filename: str
        """
        if self.barcode is None:
            self.reshape_barcode()
        # This cv2 captured video is not pickled in the json
        # therefore it is not able to be pickled for deepcopy
        # Delete it from the object first
        self.video = None
        barcode_dict = copy.deepcopy(self.__dict__)
        barcode_dict['barcode'] = barcode_dict['barcode'].tolist()
        if self.save_frames_in_generation:
            barcode_dict['saved_frames'] = barcode_dict['saved_frames'].tolist()
        if isinstance(self, ColorBarcode):
            barcode_dict['colors'] = barcode_dict['colors'].tolist()
            barcode_type = "Color"
        elif isinstance(self, BrightnessBarcode):
            barcode_dict['brightness'] = barcode_dict['brightness'].tolist()
            barcode_type = 'Brightness'
        barcode_dict["video"] = None

        if filename is None:
            filename = "saved_{:s}_barcode_{:s}_{:s}.json" \
                .format(barcode_type, self.frame_type, self.color_metric)

        with open(filename, "w") as file:
            json.dump(barcode_dict, file)
        file.close()


class ColorBarcode(Barcode):
    """
    Color barcode

    :param color_metric: The metric for computing the color of the frame
    :type color_metric: str
    :param frame_type: The type of frame sampling
    :type frame_type: str
    :param sampled_frame_rate: Frame sample rate: the frame sampled from every sampled_frame_rate.
    :type sampled_frame_rate: int
    :param skip_over: The number of frames to skip with at the beginning of the video
    :type skip_over: int
    :param total_frames: The total number of frames (computed) included in the barcode
    :type total_frames: int
    :param barcode_type: The type of the barcode
    :type barcode_type: str
    """

    def __init__(self, color_metric, frame_type, sampled_frame_rate=1, skip_over=0, total_frames=10,
                 barcode_type="Color"):
        """
        Initialize the barcode with the given parameters
        """
        super().__init__(color_metric, frame_type, sampled_frame_rate, skip_over, total_frames, barcode_type)
        self.colors = None

    def collect_colors(self, video_path_name):
        """
        Collect the colors of frames from the video

        :param video_path_name: The path to the video file
        :type video_path_name: str
        """
        self.read_video(video_path_name)

        success, frame = self.video.read()

        used_frames = 0
        cur_frame_idx = 0 + self.skip_over

        self.video.set(cv2.CAP_PROP_POS_FRAMES, cur_frame_idx)

        colors_sequence = []

        while success and used_frames < self.total_frames and cur_frame_idx < self.film_length_in_frames:
            if (cur_frame_idx % self.sampled_frame_rate) == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if self.save_frames_in_generation:
                    self.save_frames(used_frames, frame)
                frame = self.process_frame(frame)
                if len(frame.shape) <= 2:
                    frame = frame.reshape(-1, 1, 3)

                color = self.get_color_from_frame(frame)
                colors_sequence.append(color)

                used_frames += 1

            cur_frame_idx += 1

            success, frame = self.video.read()

        self.colors = np.array(colors_sequence).astype("uint8")
        if self.save_frames_in_generation:
            self.saved_frames = np.array(self.saved_frames)

    def multi_thread_collect_colors(self, video_path_name, num_thread=4):
        """
        Collect the color of the input video using Multi-thread method

        :param video_path_name: The path to the input video
        :type video_path_name: str
        :param num_thread: Number of threads to collect the brightness
        :type num_thread: int
        """
        # Correct the total frames temporarily for the multi-thread generation in order to
        # be according with the definition of total frames in single thread generation
        # where total frames == self.colors.size / 3 (channels)
        self.total_frames *= self.sampled_frame_rate
        self.read_video(video_path_name)

        thread_videos = [None] * num_thread
        thread_videos[0] = self.video
        for i in range(1, num_thread):
            thread_videos[i] = cv2.VideoCapture(video_path_name)

        threads = [None] * num_thread
        thread_results = [None] * num_thread
        step = self.total_frames // num_thread

        if self.save_frames_in_generation:
            saved_frame_results = [[]] * num_thread
        else:
            saved_frame_results = None

        for i, tid in zip(range(self.skip_over, self.skip_over + self.total_frames, step),
                          range(num_thread)):
            if tid == num_thread - 1:
                start_point = i
                break
            threads[tid] = threading.Thread(target=self.thread_collect_color_start_to_end,
                                            args=(thread_videos[tid], i, step, thread_results, tid,
                                                  saved_frame_results))
            threads[tid].start()

        threads[num_thread - 1] = threading.Thread(target=self.thread_collect_color_start_to_end,
                                                   args=(thread_videos[tid], start_point,
                                                         self.total_frames + self.skip_over - start_point,
                                                         thread_results, tid, saved_frame_results))
        threads[num_thread - 1].start()

        for i in range(num_thread):
            threads[i].join()

        # Now change the total frames back to the original input
        self.total_frames = int(self.total_frames / self.sampled_frame_rate)

        colors_sequence = [thread_results[0]]
        for i in range(1, num_thread):
            colors_sequence.append(thread_results[i])

        self.colors = np.concatenate(colors_sequence).astype("uint8")

        if self.save_frames_in_generation:
            for frame_arry in saved_frame_results:
                self.saved_frames += frame_arry
            self.saved_frames = np.array(self.saved_frames)

    def thread_collect_color_start_to_end(self, video, start_point, num_frames, results, tid, frame_saved=None):
        """
        Collect the colors from the video using the multi-threads

        :param video: The video object
        :type video: class:`cv2.VideoCapture`
        :param start_point: Start point for collecting the colors
        :type start_point: int
        :param num_frames: The number of frames to collect
        :type num_frames: int
        :param results: The placeholder for saving the results
        :type results: list
        :param tid: The id of the thread
        :type tid: int
        :param frame_saved: The placeholder for the saved frames
        :type frame_saved: list
        """
        assert self.video is not None, "No video is read in to the barcode for analysis."
        cur_frame_idx = start_point
        video.set(cv2.CAP_PROP_POS_FRAMES, cur_frame_idx)

        colors_sequence = []
        frame_sequence = []

        success, frame = video.read()
        used_frames = 0
        while success and used_frames < num_frames and cur_frame_idx < (start_point + num_frames):
            if (cur_frame_idx % self.sampled_frame_rate) == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if self.save_frames_in_generation:
                    self.save_frames(used_frames, frame, frame_sequence)
                frame = self.process_frame(frame)
                if len(frame.shape) <= 2:
                    frame = frame.reshape(-1, 1, 3)

                color = self.get_color_from_frame(frame)
                colors_sequence.append(color)

                used_frames += 1

            cur_frame_idx += 1

            success, frame = video.read()

        results[tid] = colors_sequence
        if self.save_frames_in_generation:
            frame_saved[tid] = frame_sequence

    def reshape_barcode(self, frames_per_column=160):
        """
        Reshape the barcode (2 dimensional with 3 channels)

        :param frames_per_column: Number of frames per column in the reshaped barcode
        :type frames_per_column: int
        """
        if len(self.colors) % frames_per_column == 0:
            self.barcode = self.colors.reshape(frames_per_column, -1, self.colors.shape[-1], order='F')
        elif len(self.colors) < frames_per_column:
            self.barcode = self.colors.reshape(-1, 1, self.colors.shape[-1], order='F')
        else:
            truncate_bound = int(len(self.colors) / frames_per_column) * frames_per_column
            self.barcode = self.colors[:truncate_bound].reshape(frames_per_column, -1,
                                                                self.colors.shape[-1], order='F')


class BrightnessBarcode(Barcode):
    """
    Brightness Barcode Class.

    :param color_metric: The metric for computing the color of the frame
    :type color_metric: str
    :param frame_type: The type of frame sampling
    :type frame_type: str
    :param sampled_frame_rate: Frame sample rate: the frame sampled from every sampled_frame_rate.
    :type sampled_frame_rate: int
    :param skip_over: The number of frames to skip with at the beginning of the video
    :type skip_over: int
    :param total_frames: The total number of frames (computed) included in the barcode
    :type total_frames: int
    :param barcode_type: The type of the barcode
    :type barcode_type: str
    """

    def __init__(self, color_metric, frame_type, sampled_frame_rate=1, skip_over=0, total_frames=10,
                 barcode_type="Brightness"):
        """
        Initialize the barcode with the given parameters
        """
        super().__init__(color_metric, frame_type, sampled_frame_rate, skip_over, total_frames, barcode_type)
        self.brightness = None

    def collect_brightness(self, video_path_name):
        """
        Collect the brightness from the input video

        :param video_path_name: The path to the video
        :type video_path_name: str
        """
        self.read_video(video_path_name)

        success, frame = self.video.read()

        used_frames = 0
        cur_frame_idx = 0 + self.skip_over

        self.video.set(cv2.CAP_PROP_POS_FRAMES, cur_frame_idx)

        brightness_sequence = []

        while success and used_frames < self.total_frames and cur_frame_idx < self.film_length_in_frames:
            if (cur_frame_idx % self.sampled_frame_rate) == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if self.save_frames_in_generation:
                    self.save_frames(used_frames, frame)
                frame = self.process_frame(frame)
                if len(frame.shape) <= 2:
                    frame = frame.reshape(-1, 1, 3)

                if self.color_metric in color_metrics[-2:]:
                    color = self.get_color_from_frame(frame)
                    brightness = np.sum(color * np.array([0.299, 0.587, 0.114], dtype="float64"))
                    brightness = brightness.astype("uint8")
                    brightness_sequence.append(brightness)
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    brightness = self.get_color_from_frame(frame)
                    brightness_sequence.append(brightness)

                used_frames += 1

            cur_frame_idx += 1

            success, frame = self.video.read()

        self.brightness = np.array(brightness_sequence).astype("uint8")
        if self.save_frames_in_generation:
            self.saved_frames = np.array(self.saved_frames)

    def multi_thread_collect_brightness(self, video_path_name, num_thread=4):
        """
        Collect the brightness of the input video using Multi-thread method

        :param video_path_name: The path to the input video
        :type video_path_name: str
        :param num_thread: Number of threads to collect the brightness
        :type num_thread: int
        """
        # Correct the total frames temporarily for the multi-thread generation in order to
        # be according with the definition of total frames in single thread generation
        # where total frames == self.colors.size / 3 (channels)
        self.total_frames *= self.sampled_frame_rate
        self.read_video(video_path_name)

        thread_videos = [None] * num_thread
        thread_videos[0] = self.video
        for i in range(1, num_thread):
            thread_videos[i] = cv2.VideoCapture(video_path_name)

        threads = [None] * num_thread
        thread_results = [None] * num_thread
        step = self.total_frames // num_thread

        if self.save_frames_in_generation:
            saved_frame_results = [[]] * num_thread
        else:
            saved_frame_results = None

        for i, tid in zip(range(self.skip_over, self.skip_over + self.total_frames, step),
                          range(num_thread)):
            if tid == num_thread - 1:
                start_point = i
                break
            threads[tid] = threading.Thread(target=self.thread_collect_brightness_start_to_end,
                                            args=(thread_videos[tid], i, step, thread_results,
                                                  tid, saved_frame_results))
            threads[tid].start()

        threads[num_thread - 1] = threading.Thread(target=self.thread_collect_brightness_start_to_end,
                                                   args=(thread_videos[tid], start_point,
                                                         self.total_frames + self.skip_over - start_point,
                                                         thread_results, tid, saved_frame_results))
        threads[num_thread - 1].start()

        for i in range(num_thread):
            threads[i].join()

        # Now change the total frames back to the original input
        self.total_frames = int(self.total_frames / self.sampled_frame_rate)

        brightness_sequence = [thread_results[0]]
        for i in range(1, num_thread):
            brightness_sequence.append(thread_results[i])

        self.brightness = np.concatenate(brightness_sequence).astype("uint8")

        if self.save_frames_in_generation:
            for frame_arry in saved_frame_results:
                self.saved_frames += frame_arry
            self.saved_frames = np.array(self.saved_frames)

    def thread_collect_brightness_start_to_end(self, video, start_point, num_frames, results, tid, frame_saved=None):
        """
        Collect the brightness from the video using the multi-threads

        :param video: The video object
        :type video: class:`cv2.VideoCapture`
        :param start_point: Start point for collecting the colors
        :type start_point: int
        :param num_frames: The number of frames to collect
        :type num_frames: int
        :param results: The placeholder for saving the results
        :type results: list
        :param tid: The id of the thread
        :type tid: int
        :param frame_saved: The placeholder for the saved frames
        :type frame_saved: list
        """
        assert self.video is not None, "No video is read in to the barcode for analysis."
        cur_frame_idx = start_point
        video.set(cv2.CAP_PROP_POS_FRAMES, cur_frame_idx)

        brightness_sequence = []
        frame_sequence = []

        success, frame = video.read()
        used_frames = 0
        while success and used_frames < num_frames and cur_frame_idx < (start_point + num_frames):
            if (cur_frame_idx % self.sampled_frame_rate) == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if self.save_frames_in_generation:
                    self.save_frames(used_frames, frame, frame_sequence)
                frame = self.process_frame(frame)
                if len(frame.shape) <= 2:
                    frame = frame.reshape(-1, 1, 3)

                if self.color_metric in color_metrics[-2:]:
                    color = self.get_color_from_frame(frame)
                    brightness = np.sum(color * np.array([0.299, 0.587, 0.114], dtype="float64"))
                    brightness = brightness.astype("uint8")
                    brightness_sequence.append(brightness)
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    brightness = self.get_color_from_frame(frame)
                    brightness_sequence.append(brightness)

                used_frames += 1

            cur_frame_idx += 1

            success, frame = video.read()

        results[tid] = brightness_sequence
        if self.save_frames_in_generation:
            frame_saved[tid] = frame_sequence

    def reshape_barcode(self, frames_per_column=160):
        """
        Reshape the brightness barcode (2 dimensional with 1 channel)

        :param frames_per_column: Number of frames per column in the reshaped barcode
        :type frames_per_column: int
        """
        if len(self.brightness) % frames_per_column == 0:
            self.barcode = self.brightness.reshape(frames_per_column, -1, order='F')
        elif len(self.brightness) < frames_per_column:
            self.barcode = self.brightness.reshape(-1, 1, order='F')
        else:
            truncate_bound = int(len(self.brightness) / frames_per_column) * frames_per_column
            self.barcode = self.brightness[:truncate_bound].reshape(frames_per_column, -1, order='F')

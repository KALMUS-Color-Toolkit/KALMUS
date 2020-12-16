import src.Artist as Artist
import cv2
import numpy as np
import json
import copy


color_metrics = ["Average", "Median", "Mode", "Top-dominant", "Weighted-dominant",
                 "Brightest", "Bright"]

frame_types = ["Whole_frame", "High_contrast_region", "Low_contrast_region", "Foreground", "Background"]

barcode_types = ["Color", "Brightness"]


def build_barcode_from_json(path_to_json, barcode_type="Color"):
    assert barcode_type in barcode_types, "Invalid barcode type. The available types of " \
                                          "the barcode are {:s}".format(str(barcode_types))
    with open(path_to_json, "r") as infile:
        object_dict = json.load(infile)
    infile.close()

    if barcode_type == "Color":
        barcode = ColorBarcode(color_metric=object_dict["color_metric"], frame_type=object_dict["frame_type"],
                               sampled_frame_rate=object_dict["sampled_frame_rate"],
                               skip_over=object_dict["skip_over"], total_frames=int(object_dict["total_frames"]))

        barcode.colors = np.array(object_dict["colors"]).astype("uint8")

    elif barcode_type == "Brightness":
        barcode = BrightnessBarcode(color_metric=object_dict["color_metric"], frame_type=object_dict["frame_type"],
                                    sampled_frame_rate=object_dict["sampled_frame_rate"],
                                    skip_over=object_dict["skip_over"], total_frames=int(object_dict["total_frames"]))

        barcode.brightness = np.array(object_dict["brightness"]).astype("uint8")

    barcode.set_letterbox_bound(object_dict["low_bound_ver"], object_dict["high_bound_ver"],
                                object_dict["low_bound_hor"], object_dict["high_bound_hor"])

    barcode.barcode = np.array(object_dict["barcode"])

    barcode.video = None

    barcode.film_length_in_frames = int(object_dict["film_length_in_frames"])

    return barcode


class BarcodeGenerator():
    def __init__(self, frame_type="Whole_frame", color_metric="Average", barcode_type="Color",
                 sampled_frame_rate=1, skip_over=0, total_frames=10):
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
        if self.barcode_type == "Color":
            self.barcode = ColorBarcode(self.color_metric, self.frame_type, self.sampled_frame_rate,
                                        self.skip_over, self.total_frames)
        elif self.barcode_type == "Brightness":
            self.barcode = BrightnessBarcode(self.color_metric, self.frame_type, self.sampled_frame_rate,
                                             self.skip_over, self.total_frames)

    def generate_barcode(self, video_file_path, user_defined_letterbox=False,
                         low_ver=-1, high_ver=-1, left_hor=-1, right_hor=-1):
        self.instantiate_barcode()
        if user_defined_letterbox:
            self.barcode.set_letterbox_bound(up_vertical_bound=high_ver, down_vertical_bound=low_ver,
                                             left_horizontal_bound=left_hor, right_horizontal_bound=right_hor)

        if self.barcode_type == "Color":
            self.barcode.collect_colors(video_file_path)
        elif self.barcode_type == "Brightness":
            self.barcode.collect_brightness(video_file_path)

    def generate_barcode_from_json(self, json_file_path, barcode_type=None):
        if barcode_type is None:
            barcode_type = self.barcode_type
        self.barcode = build_barcode_from_json(json_file_path, barcode_type=barcode_type)

    def get_barcode(self):
        return self.barcode


def get_contrast_matrix_of_labeled_image(frame):
    labels, grey_frame = Artist.watershed_segmentation(frame)
    try:
        adjacency_matrix = Artist.rag_to_matrix(Artist.get_rag(grey_frame, labels), len(np.unique(labels)))
        avg_color, _, region_sizes = Artist.color_of_regions(labels, frame)
        contrast_matrix = Artist.contrast_between_regions(avg_color, adjacency_matrix)
    except:
        contrast_matrix = np.array([[0]])
        labels = np.ones(shape=frame.shape)
    return contrast_matrix, labels


def foreback_segmentation(frame):
    fore_frame, back_frame = Artist.grabcut_foreback_segmentation(frame, start_row=0, row_size=frame.shape[0] - 1,
                                                                  start_col=frame.shape[1] // 6,
                                                                  col_size=frame.shape[1] * 2 // 3)
    return fore_frame, back_frame


def get_letter_box_bounds(frame, threshold=5):
    low_bound_ver = 0
    high_bound_ver = frame.shape[0]
    low_bound_hor = 0
    high_bound_hor = frame.shape[1]

    for i in range(0, frame.shape[0] // 2):
        color = np.average(frame[i, ...])
        if color > threshold:
            low_bound_ver = i
            break

    for i in range(frame.shape[0] - 1, frame.shape[0] // 2 - 1, -1):
        color = np.average(frame[i, ...])
        if color > threshold:
            high_bound_ver = i
            break

    for j in range(0, frame.shape[1] // 2):
        color = np.average(frame[:, j, ...])
        if color > threshold:
            low_bound_hor = j
            break

    for j in range(frame.shape[1] - 1, frame.shape[1] // 2 - 1, -1):
        color = np.average(frame[:, j, ...])
        if color > threshold:
            high_bound_hor = j
            break

    return low_bound_ver, high_bound_ver + 1, low_bound_hor, high_bound_hor + 1


class Barcode():
    def __init__(self, color_metric, frame_type, sampled_frame_rate=1, skip_over=0, total_frames=10):
        self.color_metric = color_metric
        self.frame_type = frame_type

        self.sampled_frame_rate = sampled_frame_rate
        self.skip_over = skip_over
        self.total_frames = total_frames

        self.video = None
        self.film_length_in_frames = 0

        self.user_defined_letterbox = False
        self.low_bound_ver = 0
        self.high_bound_ver = 0
        self.low_bound_hor = 0
        self.high_bound_hor = 0

        self.barcode = None

    def read_videos(self, video_path_name):
        self.video = cv2.VideoCapture(video_path_name)
        self.film_length_in_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        if self.total_frames > self.film_length_in_frames:
            self.total_frames = self.film_length_in_frames
        if not self.user_defined_letterbox:
            self.find_film_letterbox()

    def find_film_letterbox(self, num_sample=20):
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
                low_bound_v, high_bound_v, low_bound_h, high_bound_h = get_letter_box_bounds(frame)
                possible_low_bound_ver.append(low_bound_v)
                possible_high_bound_ver.append(high_bound_v)
                possible_low_bound_hor.append(low_bound_h)
                possible_high_bound_hor.append(high_bound_h)

        self.low_bound_ver = int(np.median(possible_low_bound_ver))
        self.high_bound_ver = int(np.median(possible_high_bound_ver))
        self.low_bound_hor = int(np.median(possible_low_bound_hor))
        self.high_bound_hor = int(np.median(possible_high_bound_hor))

    def remove_letter_box_from_frame(self, frame):
        frame = frame[self.low_bound_ver: self.high_bound_ver, self.low_bound_hor: self.high_bound_hor, ...]
        return frame

    def process_frame(self, frame):
        frame = self.remove_letter_box_from_frame(frame)

        if self.frame_type == "Whole_frame":
            processed_frame = frame
        elif self.frame_type == "High_contrast_region":
            contrast_matrix, labels = get_contrast_matrix_of_labeled_image(frame)
            highest_contrast_region = np.sum(contrast_matrix, axis=1).argmax()
            processed_frame = frame[labels == (highest_contrast_region + 1)]
        elif self.frame_type == "Low_contrast_region":
            contrast_matrix, labels = get_contrast_matrix_of_labeled_image(frame)
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

    def get_color_from_frame(self, frame):
        if self.color_metric == "Average":
            color = Artist.compute_mean_color(frame)
        elif self.color_metric == "Median":
            color = Artist.compute_median_color(frame)
        elif self.color_metric == "Mode":
            color, count = Artist.compute_mode_color(frame)
        elif self.color_metric == "Top-dominant":
            colors, dominances = Artist.compute_dominant_color(frame, n_clusters=3)
            pos = np.argsort(dominances)[-1]
            color = colors[pos]
        elif self.color_metric == "Weighted-dominant":
            colors, dominances = Artist.compute_dominant_color(frame, n_clusters=3)
            color = np.sum(colors * dominances.reshape(dominances.shape[0], 1), axis=0)
        elif self.color_metric == "Brightest":
            grey_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            pos = np.argwhere(grey_frame == grey_frame.max())[0]
            color = frame[pos[0], pos[1]].copy().astype("uint8")
        elif self.color_metric == "Bright":
            labels, bright_locations, domiance = Artist.find_bright_spots(frame, n_clusters=3, return_all_pos=True)
            top_bright = np.argsort(domiance)[-1]
            top_bright_pos = (labels == top_bright)[:, 0]
            pos = bright_locations[top_bright_pos]
            frame = frame[pos[:, 0], pos[:, 1]].reshape(pos.shape[0], 1, 3)
            color = Artist.compute_mean_color(frame)

        return color

    def get_barcode(self):
        if self.barcode is None:
            self.reshape_barcode()
        return self.barcode

    def set_letterbox_bound(self, up_vertical_bound, down_vertical_bound,
                            left_horizontal_bound, right_horizontal_bound):
        self.enable_user_defined_letterbox()
        self.low_bound_ver = up_vertical_bound
        self.high_bound_ver = down_vertical_bound
        self.low_bound_hor = left_horizontal_bound
        self.high_bound_hor = right_horizontal_bound

    def enable_user_defined_letterbox(self):
        self.user_defined_letterbox = True

    def automatic_find_letterbox(self):
        self.find_film_letterbox()

    def save_as_json(self, filename=None):
        if self.barcode is None:
            self.reshape_barcode()
        # This cv2 captured video is not pickled therefore not able to be pickled for deepcopy
        # Delete it from the object first
        self.video = None
        barcode_dict = copy.deepcopy(self.__dict__)
        barcode_dict['barcode'] = barcode_dict['barcode'].tolist()
        if isinstance(self, ColorBarcode):
            barcode_dict['colors'] = barcode_dict['colors'].tolist()
            barcode_type = "Color"
        elif isinstance(self, BrightnessBarcode):
            barcode_dict['brightness'] = barcode_dict['brightness'].tolist()
            barcode_type = 'Brightness'
        barcode_dict["video"] = None

        if filename is None:
            filename = "saved_{:s}_barcode_{:s}_{:s}.json"\
                .format(barcode_type, self.frame_type, self.color_metric)

        with open(filename, "w") as file:
            json.dump(barcode_dict, file)
        file.close()


class ColorBarcode(Barcode):
    def __init__(self, color_metric, frame_type, sampled_frame_rate=1, skip_over=0, total_frames=10):
        super().__init__(color_metric, frame_type, sampled_frame_rate, skip_over, total_frames)
        self.colors = None

    def collect_colors(self, video_path_name):
        self.read_videos(video_path_name)

        success, frame = self.video.read()

        used_frames = 0
        cur_frame_idx = 0 + self.skip_over

        self.video.set(cv2.CAP_PROP_POS_FRAMES, cur_frame_idx)

        colors_sequence = []

        while success and used_frames < self.total_frames and cur_frame_idx < self.film_length_in_frames:
            if (cur_frame_idx % self.sampled_frame_rate) == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = self.process_frame(frame)
                if len(frame.shape) <= 2:
                    frame = frame.reshape(-1, 1, 3)

                color = self.get_color_from_frame(frame)
                colors_sequence.append(color)

                used_frames += 1

            cur_frame_idx += 1

            success, frame = self.video.read()

        self.colors = np.array(colors_sequence).astype("uint8")

    def reshape_barcode(self, frames_per_column=160):
        if len(self.colors) % frames_per_column == 0:
            self.barcode = self.colors.reshape(frames_per_column, -1, self.colors.shape[-1], order='F')
        else:
            truncate_bound = int(len(self.colors) / frames_per_column) * frames_per_column
            self.barcode = self.colors[:truncate_bound].reshape(frames_per_column, -1,
                                                                self.colors.shape[-1], order='F')


class BrightnessBarcode(Barcode):
    def __init__(self, color_metric, frame_type, sampled_frame_rate=1, skip_over=0, total_frames=10):
        super().__init__(color_metric, frame_type, sampled_frame_rate, skip_over, total_frames)
        self.brightness = None

    def collect_brightness(self, video_path_name):
        self.read_videos(video_path_name)

        success, frame = self.video.read()

        used_frames = 0
        cur_frame_idx = 0 + self.skip_over

        self.video.set(cv2.CAP_PROP_POS_FRAMES, cur_frame_idx)

        brightness_sequence = []

        while success and used_frames < self.total_frames and cur_frame_idx < self.film_length_in_frames:
            if (cur_frame_idx % self.sampled_frame_rate) == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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

    def reshape_barcode(self, frames_per_column=160):
        if len(self.brightness) % frames_per_column == 0:
            self.barcode = self.brightness.reshape(frames_per_column, -1, order='F')
        else:
            truncate_bound = int(len(self.brightness) / frames_per_column) * frames_per_column
            self.barcode = self.brightness[:truncate_bound].reshape(frames_per_column, -1, order='F')

################################################## Refactor this part ##########################################

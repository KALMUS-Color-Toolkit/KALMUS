""" Image Comparison Utility """

import Bio.pairwise2 as sequence_align
import numpy as np
from skimage.color import rgb2hsv
from skimage.metrics import mean_squared_error, structural_similarity


def nrmse_similarity(image_1, image_2, norm_mode="Min max"):
    """
    Normalized root mean squared error (NRMSE).

    :param image_1: The image 1 for comparison
    :type image_1: numpy.ndarray
    :param image_2: The image 2 for comparison
    :type image_2: numpy.ndarray
    :param norm_mode: The mode for the normalization, average mode use the max (||image_1||, ||image_2||) \
                 Min max use the max(image_1 value range, image_2 value range)
    :type norm_mode: str
    :return: The score that measure the similarity between two images in range [0,1] using NRMSE \
             0 is the least similar, 1 is the most similar (same)
    :rtype: float
    """
    image_1 = image_1.astype("float64")
    image_2 = image_2.astype("float64")
    if norm_mode == "Average norm":
        image_1_avg_norm = np.sqrt(np.mean(image_1 * image_1))
        image_2_avg_norm = np.sqrt(np.mean(image_2 * image_2))
        denom = max(image_1_avg_norm, image_2_avg_norm)
    elif norm_mode == "Min max":
        image_1_min_max = image_1.max() - image_1.min()
        image_2_min_max = image_2.max() - image_1.min()
        denom = max(image_1_min_max, image_2_min_max)

    score = 1 - np.sqrt(mean_squared_error(image_1, image_2)) / denom

    return score


def ssim_similarity(image_1, image_2, window_size=None):
    """
    Structural similarity index measure (ssim)

    :param image_1: The image 1 for comparison
    :type image_1: numpy.ndarray
    :param image_2: The image 2 for comparison
    :type image_2: numpy.ndarray
    :param window_size: The size of the local window, integer
    :type window_size: int
    :return: The Structural similarity index score in range [0,1] \
             0 is the least similar, 1 is the most similar (same)
    :rtype: float
    """
    assert image_1.shape == image_2.shape, "The shape of two images used for computing structural similarity must " \
                                           "be the same."
    assert len(image_1.shape) >= 2, "The image must be a 2D image (single channel greyscale image or multi-channel" \
                                    "color image)"
    if window_size is not None:
        assert window_size % 2 == 1 and window_size < min(image_1.shape[0], image_1.shape[1]), \
            "The size of the local window must be an odd number and smaller than the size of input images"
    image_1 = image_1.astype("float64")
    image_2 = image_2.astype("float64")

    if len(image_1.shape) == 2:
        score = structural_similarity(image_1, image_2, win_size=window_size, multichannel=False)
    elif len(image_1.shape) > 2:
        score = structural_similarity(image_1, image_2, win_size=window_size, multichannel=True)

    # Renormalize [-1, 1] score to [0, 1] range
    score += 1
    score /= 2

    return score


def get_resample_index(num_frames, sample_amount=10):
    """
    Helper function
    Get the resample indexes based on the number of frames in sequences and the amount of samples we want to
    extract. The indexes are equally spaced. (linear interpolation)

    :param num_frames: The total number of frames
    :type num_frames: int
    :param sample_amount: How many frames that you want to sample from them
    :type sample_amount: int
    :return: np.array of indexes that are equally spaced from 0. The size of the array == sample_amount
    """
    assert num_frames >= sample_amount, "The number of data in"

    possible_index = np.arange(0, num_frames, (num_frames - 1) / (sample_amount - 1))

    nearest_int_index = np.round(possible_index)
    nearest_int_index[-1] = num_frames - 1

    return nearest_int_index.astype('int64')


def cross_correlation(signal_template, signal_source):
    """
    Signal matching. Cross correlation of two input signals. Signals need to be in the same shape

    :param signal_template: The template signal
    :type signal_template: numpy.ndarray
    :param signal_source: The source signal
    :type signal_source: numpy.ndarray
    :return: The cross correlation between two input signals. High cross correlation means high similarity between \
             two input signals. range in [-1, 1]
    :rtype: float
    """
    assert signal_template.shape == signal_source.shape, "The shape of two input signals/color barcodes must have the" \
                                                         "same shapes."
    template = signal_template.copy().astype("float64")
    source = signal_source.copy().astype("float64")
    template -= np.mean(signal_template, axis=tuple(np.arange(len(signal_template.shape) - 1)))
    source -= np.mean(signal_source, axis=tuple(np.arange(len(signal_template.shape) - 1)))
    nom = np.sum(template * source)
    denom = np.sqrt(np.sum(template * template)) * np.sqrt(np.sum(source * source))
    cross_corre = nom / denom

    return cross_corre


def local_cross_correlation(signal_template, signal_source, horizontal_interval=40, vertical_interval=40):
    """
    Local cross correlation between two input signals. The input signals need to be 2 dimensional for local windowing

    :param signal_template: The template signal
    :type signal_template: numpy.ndarray
    :param signal_source: The source signal
    :type signal_source: numpy.ndarray
    :param horizontal_interval: Number of horizontal intervals (window width == signal width // horizontal intervals)
    :type horizontal_interval: int
    :param vertical_interval: Number of vertical intervals (window height == signal height // vertical intervals)
    :type vertical_interval: int
    :return: The local cross correlation between two signals. Higher local cross correlation means higher similarity \
             between two signals. range in [-1, 1]
    :rtype: float
    """
    assert signal_source.shape == signal_template.shape, "Incompatiable shape between source and template signals"
    assert len(signal_source.shape) >= 2, "local cross correlation requires the input signals to be 2 dimensional"
    interval_row = signal_template.shape[0] // vertical_interval
    interval_col = signal_template.shape[1] // horizontal_interval

    if interval_row == 0:
        interval_row = 1
    if interval_col == 0:
        interval_col = 1

    template = signal_template.copy().astype("float64")
    source = signal_source.copy().astype("float64")
    for start_row in range(0, template.shape[0], interval_row):
        for start_col in range(0, template.shape[1], interval_col):
            template[start_row: start_row + interval_row, start_col: start_col + interval_col, ...] -= \
                np.mean(template[start_row: start_row + interval_row, start_col: start_col + interval_col, ...],
                        axis=(0, 1))
            source[start_row: start_row + interval_row, start_col: start_col + interval_col, ...] -= \
                np.mean(source[start_row: start_row + interval_row, start_col: start_col + interval_col, ...],
                        axis=(0, 1))

    nom = np.sum(template * source)
    denom = np.sqrt(np.sum(template ** 2)) * np.sqrt(np.sum(source ** 2))
    cross_corre = nom / denom

    return cross_corre


def generate_hue_strings_from_color_barcode(color_barcode, num_interval=12):
    """
    Helper function
    Generate the characters strings that represent the hue values of the input RGB color barcode (3 channel in range
    [0, 255]).

    :param color_barcode: Input color barcode, the input barcode must be a 1 dimensional color barcode with \
                          ``kalmus.barcodes.ColorBarcode.colors``
                          three channels (R, G, B). shape == [number of colors, 3]
    :type color_barcode: numpy.ndarray
    :param num_interval: The number of intervals that will be divided in the Hue ring (0 to 360 degree)
    :type num_interval: int
    :return: The string where each character represent the hue interval of the colors in the input RGB barcode
    :rtype: str
    """
    assert len(color_barcode.shape) == 2 and color_barcode.shape[-1] == 3, "The input color barcode must be a " \
                                                                           "2D array of 3-chanel RGB colors"
    color_barcode = rgb2hsv(color_barcode.reshape(-1, 1, 3)).reshape(-1, 3)
    hue_barcode = color_barcode[..., 0] * 360
    hue_barcode += 15
    hue_barcode[hue_barcode >= 360] -= 360

    interval_size = 360 / num_interval
    hue_barcode /= interval_size
    hue_barcode = hue_barcode.astype("uint16")

    string_barcode = ""

    for i in hue_barcode:
        str_code = i
        if str_code > 9:
            str_code = chr(ord("a") + (str_code - 9))
        else:
            str_code = str(str_code)
        string_barcode += str_code

    return string_barcode


def generate_brightness_string_from_brightness_barcode(brightness_barcode, num_interval=15):
    """
    Helper function
    Generate the string where each character represents the brightness interval of the brightness in the input
    brightness barcode.

    :param brightness_barcode: Input 1 dimensional brightness barcode with 1 channel. \
                               ``kalmus.barcodes.Barcode.BrightnessBarcode.brightness`` \
                               shape == [number of brightness, 1]
    :type brightness_barcode: numpy.ndarray
    :param num_interval: The number of intervals that will be divided in the brightness range [0, 255]
    :type num_interval: int
    :return: The string where each character represents the brightness interval of the brightness in the input
    :rtype: str
    """
    assert len(brightness_barcode.shape) == 2 and brightness_barcode.shape[-1] == 1, \
        "The input brightness barcode must be a 2D array with last channel to be 1"
    interval_size = 255 / num_interval
    bri_barcode = brightness_barcode[:, 0] // interval_size
    bri_barcode = bri_barcode.astype("uint16")

    string_barcode = ""
    for i in bri_barcode:
        str_code = i
        if str_code > 9:
            str_code = chr(ord("a") + (str_code - 9))
        else:
            str_code = str(str_code)
        string_barcode += str_code

    return string_barcode


def compare_needleman_wunsch(str_barcode_1, str_barcode_2, local_sequence_size=2000,
                             match_score=2, mismatch_penal=-1, gap_penal=-0.5, extending_gap_penal=-0.1,
                             normalized=False):
    """
    Compare two input character arrays/strings (barcode)'s matching score using the Needleman Wunsch method.
    Needleman Wunsch: https://www.sciencedirect.com/science/article/abs/pii/0022283670900574?via%3Dihub

    :param str_barcode_1: The input string representation of barcode 1
    :type str_barcode_1: str
    :param str_barcode_2: The input string representation of barcode 2
    :type str_barcode_2: str
    :param local_sequence_size: Divide the long barcode into several small barcode with local_sequence_size length
    :type local_sequence_size: int
    :param match_score: The score (bonus) for correctly matching character
    :type match_score: int
    :param mismatch_penal: The penalty for mismatch character
    :type mismatch_penal: int
    :param gap_penal: The penalty for gaps within matched sequence
    :type gap_penal: int
    :param extending_gap_penal: The penalty for extending gaps
    :type extending_gap_penal: int
    :param normalized: If True normalize the final matching score into range [0, 1]. If False, return the raw score
    :type normalized: bool
    :return: The match score/normalized match score
    :rtype: float
    """
    assert len(str_barcode_1) == len(str_barcode_2), "The lengths of two barcodes have to be identical"

    scores = 0
    for start_point in range(0, len(str_barcode_1), local_sequence_size):
        scores += sequence_align.align.globalms(str_barcode_1[start_point:start_point + local_sequence_size],
                                                str_barcode_2[start_point:start_point + local_sequence_size],
                                                match_score, mismatch_penal, gap_penal, extending_gap_penal,
                                                score_only=True)

    if normalized:
        denom = len(str_barcode_1) * match_score
    else:
        denom = 1

    return scores / denom


def compare_smith_waterman(str_barcode_1, str_barcode_2, local_sequence_size=2000,
                           match_score=2, mismatch_penal=-1, gap_penal=-0.5, extending_gap_penal=-0.1,
                           normalized=False):
    """
    Compare two input character arrays/strings (barcode)'s matching score using the Smith Waterman method.
    Smith Waterman: https://www.sciencedirect.com/science/article/abs/pii/0022283681900875?via%3Dihub

    :param str_barcode_1: The input string representation of barcode 1
    :type str_barcode_1: str
    :param str_barcode_2: The input string representation of barcode 2
    :type str_barcode_2: str
    :param local_sequence_size: Divide the long barcode into several small barcode with local_sequence_size length
    :type local_sequence_size: int
    :param match_score: The score (bonus) for correctly matching character
    :type match_score: int
    :param mismatch_penal: The penalty for mismatch character
    :type mismatch_penal: int
    :param gap_penal: The penalty for gaps within matched sequence
    :type gap_penal: int
    :param extending_gap_penal: The penalty for extending gaps
    :type extending_gap_penal: int
    :param normalized: If True, normalize the final matching score into range [0, 1]. If False, return the raw score.
    :type normalized: bool
    :return: The match score/normalized match score
    :rtype: float
    """
    assert len(str_barcode_1) == len(str_barcode_2), "The lengths of two barcodes have to be identical"

    scores = 0
    for start_point in range(0, len(str_barcode_1), local_sequence_size):
        scores += sequence_align.align.localms(str_barcode_1[start_point:start_point + local_sequence_size],
                                               str_barcode_2[start_point:start_point + local_sequence_size],
                                               match_score, mismatch_penal, gap_penal, extending_gap_penal,
                                               score_only=True)

    if normalized:
        denom = len(str_barcode_1) * match_score
    else:
        denom = 1

    return scores / denom

import Bio.pairwise2 as sequence_align
import numpy as np
from skimage.color import rgb2hsv
from skimage.metrics import mean_squared_error, structural_similarity


def nrmse_similarity(image_1, image_2, mode="Average norm"):
    image_1 = image_1.astype("float64")
    image_2 = image_2.astype("float64")
    if mode == "Average norm":
        image_1_avg_norm = np.sqrt(np.mean(image_1 * image_1))
        image_2_avg_norm = np.sqrt(np.mean(image_2 * image_2))
        denom = max(image_1_avg_norm, image_2_avg_norm)
    elif mode == "Min max":
        image_1_min_max = image_1.max() - image_1.min()
        image_2_min_max = image_2.max() - image_1.min()
        denom = max(image_1_min_max, image_2_min_max)

    score = 1 - np.sqrt(mean_squared_error(image_1, image_2)) / denom

    return score


def ssim_similarity(image_1, image_2, window_size=None):
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

    return score


def get_resample_index(num_frames, sample_amount=10):
    """
    Get the resample indexes based on the number of frames in sequences and the amount of samples we want to
    extract
    :param num_frames:
    :param sample_amount:
    :return:
    """
    assert num_frames >= sample_amount, "The number of data in"

    possible_index = np.arange(0, num_frames, (num_frames - 1) / (sample_amount - 1))

    nearest_int_index = np.round(possible_index)
    nearest_int_index[-1] = num_frames - 1

    return nearest_int_index.astype('int64')


def cross_correlation(signal_template, signal_source):
    assert signal_template.shape == signal_source.shape, "The shape of two input signals/color barcodes must have the" \
                                                         "same shapes."
    template = signal_template.copy()
    source = signal_source.copy()
    template -= np.mean(signal_template, axis=tuple(np.arange(len(signal_template.shape) - 1)))
    source -= np.mean(signal_source, axis=tuple(np.arange(len(signal_template.shape) - 1)))
    nom = np.sum(template * source)
    denom = np.sqrt(np.sum(template * template)) * np.sqrt(np.sum(source * source))
    # nom = np.sum(template * source) ** 2
    # denom = np.sum(template * template) * np.sum(source * source)
    cross_corre = nom / denom

    return cross_corre


def local_cross_correlation(signal_template, signal_source, horizontal_interval=40, vertical_interval=40):
    assert signal_source.shape == signal_template.shape, "Incompatiable shape between source and template signals"
    assert len(signal_source.shape) >= 2, "local cross correlation requires the input signals to be 2 dimensional"
    interval_row = signal_template.shape[0] // vertical_interval
    interval_col = signal_template.shape[1] // horizontal_interval
    template = signal_template.copy()
    source = signal_source.copy()
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


def compare_needleman_wunsch(barcode_1, barcode_2, local_sequence_size=2000,
                             match_score=2, mismatch_penal=-1, gap_penal=-0.5, extending_gap_penal=-0.1,
                             normalized=False):
    assert len(barcode_1) == len(barcode_2), "The lengths of two barcodes have to be identical"

    scores = 0
    for start_point in range(0, len(barcode_1), local_sequence_size):
        scores += sequence_align.align.globalms(barcode_1[start_point:start_point + local_sequence_size],
                                                barcode_2[start_point:start_point + local_sequence_size],
                                                match_score, mismatch_penal, gap_penal, extending_gap_penal,
                                                score_only=True)

    if normalized:
        denom = len(barcode_1) * match_score
    else:
        denom = 1

    return scores / denom


def compare_smith_waterman(barcode_1, barcode_2, local_sequence_size=2000,
                           match_score=2, mismatch_penal=-1, gap_penal=-0.5, extending_gap_penal=-0.1,
                           normalized=False):
    assert len(barcode_1) == len(barcode_2), "The lengths of two barcodes have to be identical"

    scores = 0
    for start_point in range(0, len(barcode_1), local_sequence_size):
        scores += sequence_align.align.localms(barcode_1[start_point:start_point + local_sequence_size],
                                               barcode_2[start_point:start_point + local_sequence_size],
                                               match_score, mismatch_penal, gap_penal, extending_gap_penal,
                                               score_only=True)

    if normalized:
        denom = len(barcode_1) * match_score
    else:
        denom = 1

    return scores / denom

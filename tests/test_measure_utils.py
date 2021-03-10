# Third-party modules
import pytest
import numpy as np
import matplotlib.pyplot as plt
import cv2

# kalmus module being tested
import kalmus.utils.measure_utils as measure_utils


def get_another_test_color_image():
    # A color image that is different than the shared test data
    # Used for similarity measurement
    color_image_1 = plt.imread("tests/test_data/test_color_image.jpg", format="jpeg")
    cur_image = plt.imread("tests/test_data/test_color_image_2.jpg", format="jpeg")
    # Make sure two compared image are in the same spatial size
    if color_image_1.shape[:2] !=  cur_image.shape[:2]:
        # Use INTER_NEAREST interpolation to avoid aliasing that creates artificial data
        cur_image = cv2.resize(cur_image, dsize=color_image_1.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
    return cur_image


def get_another_test_gray_image():
    # A color image that is different than the shared test data
    # Used for similarity measurement
    clr_image = plt.imread("tests/test_data/test_color_image_2.jpg", format="jpeg")
    cur_image = cv2.cvtColor(clr_image, cv2.COLOR_RGB2GRAY)
    clr_image_1 = plt.imread("tests/test_data/test_color_image.jpg", format="jpeg")
    gray_image_1 = cv2.cvtColor(clr_image_1, cv2.COLOR_RGB2GRAY)
    # Make sure two compared image are in the same spatial size
    if gray_image_1.shape[:2] != cur_image.shape[:2]:
        # Use INTER_NEAREST interpolation to avoid aliasing that creates artificial data
        cur_image = cv2.resize(cur_image, dsize=gray_image_1.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
    return cur_image


def test_nrmse_similarity(get_test_color_image, get_test_gray_image):
    color_image_1 = get_test_color_image
    # Compared to itself (should be the most similar)
    score = measure_utils.nrmse_similarity(color_image_1, color_image_1)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    color_image_2 = get_another_test_color_image()
    score = measure_utils.nrmse_similarity(color_image_1, color_image_2)
    assert np.round(score, 6) != 1

    # Compared to itself (should be the most similar) using Min max normalization
    score = measure_utils.nrmse_similarity(color_image_1, color_image_1,
                                           norm_mode="Average norm")

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    color_image_2 = get_another_test_color_image()
    score = measure_utils.nrmse_similarity(color_image_1, color_image_2,
                                           norm_mode="Average norm")
    assert np.round(score, 6) != 1

    gray_image_1 = get_test_gray_image
    # Compared to itself (should be the most similar)
    score = measure_utils.nrmse_similarity(gray_image_1, gray_image_1)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    gray_image_2 = get_another_test_gray_image()
    score = measure_utils.nrmse_similarity(gray_image_1, gray_image_2)
    assert np.round(score, 6) != 1


def test_ssim_similarity(get_test_color_image, get_test_gray_image):
    color_image_1 = get_test_color_image
    # Compared to itself (should be the most similar)
    score = measure_utils.ssim_similarity(color_image_1, color_image_1)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    color_image_2 = get_another_test_color_image()
    score = measure_utils.ssim_similarity(color_image_1, color_image_2)
    assert np.round(score, 6) != 1

    # Compared to itself (should be the most similar) with local window size=31
    score = measure_utils.ssim_similarity(color_image_1, color_image_1,
                                          window_size=31)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    color_image_2 = get_another_test_color_image()
    score = measure_utils.ssim_similarity(color_image_1, color_image_2,
                                          window_size=31)
    assert np.round(score, 6) != 1

    gray_image_1 = get_test_gray_image
    # Compared to itself (should be the most similar)
    score = measure_utils.ssim_similarity(gray_image_1, gray_image_1)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    gray_image_2 = get_another_test_gray_image()
    score = measure_utils.ssim_similarity(gray_image_1, gray_image_2)
    assert np.round(score, 6) != 1


def test_get_resample_index():
    num_indexes = 100
    num_samples = 10
    indexes = measure_utils.get_resample_index(num_indexes, num_samples)
    assert indexes[0] == 0
    # Last index == number of indexes - 1 (for 0 indexed array)
    assert indexes[-1] == num_indexes - 1
    assert len(indexes) == num_samples


def test_cross_correlation(get_test_color_image, get_test_gray_image):
    color_image_1 = get_test_color_image
    # Compared to itself (should be the most similar)
    score = measure_utils.cross_correlation(color_image_1, color_image_1)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    color_image_2 = get_another_test_color_image()
    score = measure_utils.cross_correlation(color_image_1, color_image_2)
    assert np.round(score, 6) != 1

    gray_image_1 = get_test_gray_image
    # Compared to itself (should be the most similar)
    score = measure_utils.cross_correlation(gray_image_1, gray_image_1)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    gray_image_2 = get_another_test_gray_image()
    score = measure_utils.cross_correlation(gray_image_1, gray_image_2)
    assert np.round(score, 6) != 1


def test_local_cross_correlation(get_test_color_image, get_test_gray_image):
    # Number of vertical intervals (determining local window's height)
    num_ver_inter = 10
    # Number of horizontal intervals (determing local window's width)
    num_hor_inter = 20

    color_image_1 = get_test_color_image
    # Compared to itself (should be the most similar)
    score = measure_utils.local_cross_correlation(color_image_1, color_image_1,
                                                  vertical_interval=num_ver_inter,
                                                  horizontal_interval=num_hor_inter)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    color_image_2 = get_another_test_color_image()
    score = measure_utils.local_cross_correlation(color_image_1, color_image_2,
                                                  vertical_interval=num_ver_inter,
                                                  horizontal_interval=num_hor_inter)
    assert np.round(score, 6) != 1

    gray_image_1 = get_test_gray_image
    # Compared to itself (should be the most similar)
    score = measure_utils.local_cross_correlation(gray_image_1, gray_image_1,
                                                  vertical_interval=num_ver_inter,
                                                  horizontal_interval=num_hor_inter)

    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    gray_image_2 = get_another_test_gray_image()
    score = measure_utils.local_cross_correlation(gray_image_1, gray_image_2,
                                                  vertical_interval=num_ver_inter,
                                                  horizontal_interval=num_hor_inter)
    assert np.round(score, 6) != 1


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_generate_hue_strings_from_color_barcode(get_test_color_image):
    # Here, we can use the flatten color image as a color barcode
    # as the barcode here refer to the 1 D array of colors in the barcode image
    color_barcode = get_test_color_image.reshape(-1, 3)

    # Number of intervals that we want to divide a 360-degree hue wheel
    # Each interval occupies 60 degree of hue wheel
    num_interval = 6
    hue_strings = measure_utils.generate_hue_strings_from_color_barcode(color_barcode, num_interval=num_interval)
    # Color barcode's hue values can be in at most all 6 intervals
    # but in at least 1 interval. Thus, the number of unique character in hue_strings follow this same rule
    assert 1 <= np.unique(hue_strings).size <= num_interval
    assert len(hue_strings) == color_barcode.size / color_barcode.shape[-1]


def test_generate_brightness_string_from_brightness_barcode(get_test_gray_image):
    # Here, we can use the flatten gray image as a brightness barcode
    # as the barcode here refer to the 1 D array of brightness in the barcode image
    brightness_barcode = get_test_gray_image.reshape(-1, 1)

    # Number of intervals that we want to divide a 360-degree hue wheel
    # Each interval occupies 60 degree of hue wheel
    num_interval = 5
    bri_strings = measure_utils.generate_brightness_string_from_brightness_barcode(brightness_barcode,
                                                                                   num_interval=num_interval)
    # Color barcode's hue values can be in at most all 6 intervals
    # but in at least 1 interval. Thus, the number of unique character in hue_strings follow this same rule
    assert 1 <= np.unique(bri_strings).size <= num_interval
    assert len(bri_strings) == brightness_barcode.size


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_compare_smith_waterman(get_test_color_image, get_test_gray_image):
    # Here, we can use the flatten color/gray image as a color/brightness barcode
    # as the barcode here refer to the 1 D array of color/brightness in the barcode image
    color_barcode_1 = get_test_color_image.reshape(-1, 3)
    color_barcode_2 = get_another_test_color_image().reshape(-1, 3)
    brightness_barcode_1 = get_test_gray_image.reshape(-1, 1)
    brightness_barcode_2 = get_another_test_gray_image().reshape(-1, 1)

    # Preprocessed the color/brightness array to character symbolized array
    str_color_barcode_1 = measure_utils.generate_hue_strings_from_color_barcode(color_barcode_1)
    str_color_barcode_2 = measure_utils.generate_hue_strings_from_color_barcode(color_barcode_2)
    str_brightness_barcode_1 = measure_utils.generate_brightness_string_from_brightness_barcode(brightness_barcode_1)
    str_brightness_barcode_2 = measure_utils.generate_brightness_string_from_brightness_barcode(brightness_barcode_2)

    score = measure_utils.compare_smith_waterman(str_color_barcode_1, str_color_barcode_1, normalized=True)
    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    score = measure_utils.compare_smith_waterman(str_color_barcode_1, str_color_barcode_2, normalized=True)
    assert np.round(score, 6) != 1

    score = measure_utils.compare_smith_waterman(str_brightness_barcode_1, str_brightness_barcode_1, normalized=True)
    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    score = measure_utils.compare_smith_waterman(str_brightness_barcode_1, str_brightness_barcode_2, normalized=True)
    assert np.round(score, 6) != 1


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_compare_needleman_wunsch(get_test_color_image, get_test_gray_image):
    # Here, we can use the flatten color/gray image as a color/brightness barcode
    # as the barcode here refer to the 1 D array of color/brightness in the barcode image
    color_barcode_1 = get_test_color_image.reshape(-1, 3)
    color_barcode_2 = get_another_test_color_image().reshape(-1, 3)
    brightness_barcode_1 = get_test_gray_image.reshape(-1, 1)
    brightness_barcode_2 = get_another_test_gray_image().reshape(-1, 1)

    # Preprocessed the color/brightness array to character symbolized array
    str_color_barcode_1 = measure_utils.generate_hue_strings_from_color_barcode(color_barcode_1)
    str_color_barcode_2 = measure_utils.generate_hue_strings_from_color_barcode(color_barcode_2)
    str_brightness_barcode_1 = measure_utils.generate_brightness_string_from_brightness_barcode(brightness_barcode_1)
    str_brightness_barcode_2 = measure_utils.generate_brightness_string_from_brightness_barcode(brightness_barcode_2)

    score = measure_utils.compare_needleman_wunsch(str_color_barcode_1, str_color_barcode_1, normalized=True)
    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    score = measure_utils.compare_needleman_wunsch(str_color_barcode_1, str_color_barcode_2, normalized=True)
    assert np.round(score, 6) != 1

    score = measure_utils.compare_needleman_wunsch(str_brightness_barcode_1, str_brightness_barcode_1, normalized=True)
    # Allow small precisions lost in the floating point computation
    assert np.round(score, 6) == 1

    score = measure_utils.compare_needleman_wunsch(str_brightness_barcode_1, str_brightness_barcode_2, normalized=True)
    assert np.round(score, 6) != 1

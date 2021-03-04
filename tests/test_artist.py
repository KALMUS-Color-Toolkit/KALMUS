# Third-party modules
import pytest
import numpy as np
import matplotlib.pyplot as plt
import cv2
import warnings

# Filter out the warnings raised by numpy.dtype and numpy.ufunc
# See pull requests on NumPy https://github.com/numpy/numpy/pull/432 for references about these warnings
# See https://stackoverflow.com/questions/40845304/runtimewarning-numpy-dtype-size-changed-may-indicate-binary-incompatibility
# for how the warnings are dealt in this automated test suite
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

# kalmus module being tested
import kalmus.utils.artist as artist


def get_test_color_video():
    video = cv2.VideoCapture("tests/test_data/test_color_video.mp4")
    return video


def get_test_color_image_with_letterbox():
    return plt.imread("tests/test_data/test_color_image_letterboxing.jpg", format="jpeg")


def test_compute_mean_color(get_test_color_image):
    color = artist.compute_mean_color(get_test_color_image)
    assert color.shape == (3,)


def test_compute_median_color(get_test_color_image):
    color = artist.compute_median_color(get_test_color_image)
    assert color.shape == (3,)


def test_compute_mode_color(get_test_color_image):
    image = get_test_color_image
    color, count = artist.compute_mode_color(get_test_color_image)
    assert color.shape == (3,)
    assert count.shape == (1, 3)
    assert np.all(count < image.size)


def test_compute_dominant_color(get_test_color_image):
    # Epsilon for small precision that may be lost in the floating point computation
    epsilon = 1e-6
    dominant_colors, ratio_of_dominance = artist.compute_dominant_color(get_test_color_image)
    assert dominant_colors.shape == (3, 3)
    assert 1.0 - epsilon < ratio_of_dominance.sum() < 1.0 + epsilon

    # Change to 5 clusters
    dominant_colors, ratio_of_dominance = artist.compute_dominant_color(get_test_color_image, 5)
    assert dominant_colors.shape == (5, 3)
    assert 1.0 - epsilon < ratio_of_dominance.sum() < 1.0 + epsilon


def test_compute_brightest_color_and_brightness(get_test_color_image, get_test_gray_image):
    color_image = get_test_color_image
    gray_image = get_test_gray_image
    max_color, max_brightness, max_loc = artist.compute_brightest_color_and_brightness(gray_image, color_image)
    assert np.all(max_color == color_image[max_loc])
    assert max_brightness == gray_image.max() == gray_image[max_loc]
    _, _, _, min_color, min_brightness, min_loc = artist.compute_brightest_color_and_brightness(gray_image,
                                                                                                color_image,
                                                                                                return_min=True)
    assert np.all(min_color == color_image[min_loc])
    assert min_brightness == gray_image.min() == gray_image[min_loc]


def test_find_bright_spots(get_test_color_image):
    # Epsilon for small precision that may be lost in the floating point computation
    epsilon = 1e-6

    color_image = get_test_color_image
    spots_central_location, ratio_of_dominance = artist.find_bright_spots(color_image, n_clusters=3)
    assert spots_central_location.shape == (3, 2)
    assert 1.0 - epsilon < ratio_of_dominance.sum() < 1.0 + epsilon
    assert 0 <= spots_central_location[:, 0].max() < color_image.shape[0]
    assert 0 <= spots_central_location[:, 1].max() < color_image.shape[1]

    num_clusters = 4
    labeled_locs, original_locs, ratio_of_dominance = artist.find_bright_spots(color_image,
                                                                               n_clusters=num_clusters,
                                                                               return_all_pos=True)
    assert 1.0 - epsilon < ratio_of_dominance.sum() < 1.0 + epsilon
    assert np.unique(labeled_locs).size == num_clusters
    assert original_locs.shape[0] <= color_image.size
    assert original_locs.shape[1] == 2


def test_random_sample_pixels(get_test_color_image):
    image = get_test_color_image
    sample_ratio_whole = 0.64
    ratio_each_axis = np.sqrt(sample_ratio_whole)

    # Sampled image that keep original dimension
    sampled_2D = artist.random_sample_pixels(image, sample_ratio=sample_ratio_whole, mode="row-col")
    # Small lose in spatial size when resampling image that has discrete number of rows and columns
    epsilon = 0.005
    assert image.shape[0] * (ratio_each_axis - epsilon) < sampled_2D.shape[0] < image.shape[0] * (ratio_each_axis + epsilon)
    assert image.shape[1] * (ratio_each_axis - epsilon) < sampled_2D.shape[1] < image.shape[1] * (ratio_each_axis + epsilon)

    # Sampled out pixels (lose dimensions)
    sampled_1D = artist.random_sample_pixels(image, sample_ratio=sample_ratio_whole, mode="flat")
    # Potential small loses in size when resampling discrete/integer number of pixels
    epsilon = 1e-5
    assert image.size * (sample_ratio_whole - epsilon) < sampled_1D.size < image.size * (sample_ratio_whole + epsilon)


def test_watershed_segmentation(get_test_color_image):
    color_image = get_test_color_image
    segmented_image, gray_image = artist.watershed_segmentation(color_image)
    assert segmented_image.shape == gray_image.shape == color_image.shape[:2]


def test_color_of_regions(get_test_color_image):
    color_image = get_test_color_image
    segmented_image, gray_image = artist.watershed_segmentation(color_image)
    avg_colors, brightest_colors, region_size_ratio = artist.color_of_regions(segmented_image, color_image)

    assert np.array(avg_colors).shape[0] == np.unique(segmented_image).size
    assert np.array(brightest_colors).shape[0] == np.unique(segmented_image).size
    # Epsilon for small precision that may be lost in the floating point computation
    epsilon = 1e-6
    assert 1.0 - epsilon < np.sum(region_size_ratio) < 1.0 + epsilon


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_contrast_between_regions(get_test_color_image):
    color_image = get_test_color_image
    segmented_image, gray_image = artist.watershed_segmentation(color_image)
    avg_colors, brightest_colors, region_size_ratio = artist.color_of_regions(segmented_image, color_image)

    rag = artist.get_rag(gray_image, segmented_image)
    num_regions= np.unique(segmented_image).size
    matrix = artist.rag_to_matrix(rag, num_regions=num_regions)

    contrast_matrix = artist.contrast_between_regions(avg_colors, matrix)
    assert contrast_matrix.shape == (num_regions, num_regions)
    contrast_matrix_weighted = artist.contrast_between_regions(brightest_colors, matrix,
                                                               region_weights=region_size_ratio)
    assert contrast_matrix_weighted.shape == (num_regions, num_regions)


def test_contrast_ratio():
    color_1 = np.array([125, 125, 125])
    color_2 = np.array([125, 125, 125])
    color_3 = np.array([250, 250, 250])

    contrast_1 = artist.contrast_ratio(color_1, color_2)
    assert contrast_1 == 1

    contrast_2 = artist.contrast_ratio(color_1, color_3)
    assert contrast_2 != 1


def test_grabcut_foreback_segmentation(get_test_color_image):
    color_image = get_test_color_image
    foreground, background = artist.grabcut_foreback_segmentation(color_image)
    assert foreground.size + background.size == color_image.size
    assert foreground.shape[-1] == background.shape[-1] == color_image.shape[-1]

    foreground_mask, background_mask = artist.grabcut_foreback_segmentation(color_image, return_masks=True)
    assert foreground_mask.shape == background_mask.shape == color_image.shape[:2]


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_get_contrast_matrix_and_labeled_image(get_test_color_image):
    color_image = get_test_color_image
    matrix, labeled_image = artist.get_contrast_matrix_and_labeled_image(color_image)
    assert labeled_image.shape == color_image.shape[:2]
    num_of_regions = np.unique(labeled_image).shape[0]
    assert matrix.shape == (num_of_regions, num_of_regions)


def test_get_letter_box_from_frames():
    color_image = get_test_color_image_with_letterbox()
    small_row_bound, large_row_bound, small_col_bound, large_col_bound = artist.get_letter_box_from_frames(color_image)
    # Observed bounds for letterbox in this frame
    assert small_row_bound == 54
    assert large_row_bound == 422
    assert small_col_bound == 0
    assert large_col_bound == 847


def test_find_letter_box_from_videos():
    video = get_test_color_video()
    small_row_bound, large_row_bound, small_col_bound, large_col_bound = artist.find_letter_box_from_videos(video)
    # find_letter_box_frame find the exact locations of letterbox on a subset of frames (sampled out frames)
    # Since frames are randomly sampled each time, allow small variations in final results
    epsilon = 2
    assert 80 - epsilon < small_row_bound < 80 + epsilon
    assert 634 - epsilon < large_row_bound < 634 + epsilon
    assert 3 - epsilon < small_col_bound < 3 + epsilon
    assert 1274 - epsilon < large_col_bound < 1274 + epsilon

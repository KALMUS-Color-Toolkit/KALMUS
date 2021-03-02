# Third-party modules
import pytest
import numpy as np
import matplotlib.pyplot as plt
import cv2

# kalmus module being tested
import kalmus.utils.artist as artist


@pytest.fixture(scope="session")
def get_test_color_image():
    return plt.imread("automated_tests/test_data/test_color_image.jpg", format='jpeg')


@pytest.fixture(scope="session")
def get_test_gray_image():
    clr_image = plt.imread("automated_tests/test_data/test_color_image.jpg", format='jpeg')
    gray_image = cv2.cvtColor(clr_image, cv2.COLOR_RGB2GRAY)
    return gray_image


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

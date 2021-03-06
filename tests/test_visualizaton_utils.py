# Third-party modules
import pytest
import numpy as np
import matplotlib.pyplot as plt

# kalmus module being tested
import kalmus.utils.visualization_utils as visualization_utils


def test_show_color():
    color = np.array([1, 2, 3])
    color_image = visualization_utils.show_color(color, return_color=True)
    assert color_image.shape == (30, 30, 3)


def test_show_colors_in_sequence():
    color_sequence = np.array([[1, 2, 3], [4, 5, 6]])
    color_sequence_image = visualization_utils.show_colors_in_sequence(color_sequence, return_color_sequence=True)
    assert color_sequence_image.shape == (30, 30 * color_sequence.shape[0], 3)


def test_show_color_matrix(get_test_color_image):
    color_2d_image = get_test_color_image
    color_matrix = visualization_utils.show_color_matrix(color_2d_image, return_matrix=True, mode="padding")
    assert color_matrix.shape == (color_2d_image.shape[1], color_2d_image.shape[0] + 1, color_2d_image.shape[2])

    color_matrix = visualization_utils.show_color_matrix(color_2d_image, return_matrix=True, mode="truncate")
    assert color_matrix.shape == (color_2d_image.shape[1], color_2d_image.shape[0], color_2d_image.shape[2])

    figure = visualization_utils.show_color_matrix(color_2d_image, return_figure=True)
    assert isinstance(figure, plt.Figure)


def test_show_colors_in_cube(get_test_color_image):
    flatten_image = get_test_color_image.reshape(-1, 3)
    sampled_colors = visualization_utils.show_colors_in_cube(flatten_image, sampling=-1, return_sampled_colors=True)
    assert sampled_colors.size == flatten_image.size

    samples = 100
    sampled_colors = visualization_utils.show_colors_in_cube(flatten_image, sampling=samples, return_sampled_colors=True)
    assert sampled_colors.size == samples * sampled_colors.shape[-1]

    fig, ax = visualization_utils.show_colors_in_cube(flatten_image, sampling=samples, return_figure=True)
    assert isinstance(fig, plt.Figure)
    assert isinstance(ax, plt.Axes)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_show_high_contrast_region(get_test_color_image):
    color_image = get_test_color_image
    image_with_high_contrast_region = visualization_utils.show_high_contrast_region(color_image,
                                                                                    return_region_image=True)
    assert color_image.shape == image_with_high_contrast_region.shape


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_show_low_contrast_region(get_test_color_image):
    color_image = get_test_color_image
    image_with_low_contrast_region = visualization_utils.show_low_contrast_region(color_image,
                                                                                  return_region_image=True)
    assert color_image.shape == image_with_low_contrast_region.shape


def test_extract_region_with_index(get_test_color_image):
    color_image = get_test_color_image
    # Make an artificial label mask with three regions (indexed with 0, 1, 2)
    mask = np.zeros(shape=color_image.shape[:2])
    mask[:, mask.shape[1] // 3: mask.shape[1] * 2 // 3] = 1
    mask[:, mask.shape[1] * 2 // 3:] = 2

    region_index = 1
    image_with_extracted_region_only = visualization_utils.extract_region_with_index(color_image, region_index, mask)
    assert image_with_extracted_region_only.shape == color_image.shape
    assert np.all(image_with_extracted_region_only[mask == region_index] == color_image[mask == region_index])

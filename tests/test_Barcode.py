# Third-party modules
import pytest
import matplotlib.pyplot as plt
import warnings
import numpy as np
import cv2

# Filter out the warnings raised by numpy.dtype and numpy.ufunc
# See pull requests on NumPy https://github.com/numpy/numpy/pull/432 for references about these warnings
# See https://stackoverflow.com/questions/40845304/runtimewarning-numpy-dtype-size-changed-may-indicate-binary-incompatibility
# for how the warnings are dealt in this automated test suite
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

# kalmus module being tested
import kalmus.barcodes.Barcode as BarcodeClasses


def get_template_barcode():
    return BarcodeClasses.Barcode(color_metric="average", frame_type="whole_frame", barcode_type="Color")


def test_foreback_segmentation(get_test_color_image):
    color_image = get_test_color_image
    fore, back = BarcodeClasses.foreback_segmentation(color_image)
    assert fore.size + back.size == color_image.size
    assert fore.shape[-1] == back.shape[-1] == color_image.shape[-1]


def test_Barcode():
    barcode = BarcodeClasses.Barcode(color_metric="average", frame_type="whole_frame", sampled_frame_rate=2,
                                     skip_over=10, total_frames=100, barcode_type="color")
    assert barcode.color_metric == "Average"
    assert barcode.frame_type == "Whole_frame"
    assert barcode.barcode_type == "Color"
    assert barcode.sampled_frame_rate == 2
    assert barcode.skip_over == 10
    assert barcode.total_frames == 100


def test_read_video():
    barcode = get_template_barcode()
    barcode.read_video("tests/test_data/test_color_video.mp4")
    assert isinstance(barcode.video, cv2.VideoCapture)
    assert barcode.fps > 0
    assert barcode.film_length_in_frames > 0

    barcode.total_frames = 1e6
    barcode.save_frames_in_generation = True
    barcode.enable_save_frames()
    barcode.read_video("tests/test_data/test_color_video.mp4")
    assert barcode.total_frames == barcode.film_length_in_frames - barcode.skip_over
    assert barcode.high_bound_hor != 0
    assert barcode.low_bound_ver != 0
    assert barcode.saved_frames_sampled_rate > 0


def test_find_film_letter_box():
    barcode = get_template_barcode()
    barcode.read_video("tests/test_data/test_color_video.mp4")
    barcode.find_film_letterbox()
    assert barcode.high_bound_hor != 0
    assert barcode.high_bound_ver != 0


def test_remove_letter_box_from_frame(get_test_color_image):
    color_frame = get_test_color_image
    barcode = get_template_barcode()
    barcode.read_video("tests/test_data/test_color_video.mp4")

    barcode.low_bound_ver = 10
    barcode.high_bound_ver = color_frame.shape[0] - 10
    barcode.low_bound_hor = 10
    barcode.high_bound_hor = color_frame.shape[1] - 10

    cropped_frame = barcode.remove_letter_box_from_frame(color_frame)
    assert cropped_frame.shape[0] == barcode.high_bound_ver - barcode.low_bound_ver
    assert cropped_frame.shape[1] == barcode.high_bound_hor - barcode.low_bound_hor
    assert cropped_frame.shape[-1] == color_frame.shape[-1]


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_process_frame(get_test_color_image):
    color_frame = get_test_color_image
    barcode = get_template_barcode()

    barcode.low_bound_ver = 0
    barcode.high_bound_ver = color_frame.shape[0]
    barcode.low_bound_ver = 0
    barcode.high_bound_hor = color_frame.shape[1]

    barcode.frame_type = "Whole_frame"
    processed_frame = barcode.process_frame(color_frame)
    assert np.all(processed_frame == color_frame)

    barcode.frame_type = "High_contrast_region"
    processed_frame = barcode.process_frame(color_frame)
    assert processed_frame.shape[-1] == color_frame.shape[-1]
    assert len(processed_frame.shape) == 2

    barcode.frame_type = "Low_contrast_region"
    processed_frame = barcode.process_frame(color_frame)
    assert processed_frame.shape[-1] == color_frame.shape[-1]
    assert len(processed_frame.shape) == 2

    barcode.frame_type = "Foreground"
    processed_frame = barcode.process_frame(color_frame)
    assert processed_frame.shape[-1] == color_frame.shape[-1]
    assert len(processed_frame.shape) == 2

    barcode.frame_type = "Background"
    processed_frame = barcode.process_frame(color_frame)
    assert processed_frame.shape[-1] == color_frame.shape[-1]
    assert len(processed_frame.shape) == 2


def test_resize_frame(get_test_color_image):
    color_image = get_test_color_image
    barcode = get_template_barcode()
    barcode.rescale_frame_factor = 2

    resize_frame = barcode._resize_frame(color_image)
    # Allow small precision lost in resize (resampling) frame
    epsilon = 1e-2
    assert color_image.shape[0] * (barcode.rescale_frame_factor - epsilon) < resize_frame.shape[0] < \
           color_image.shape[0] * (barcode.rescale_frame_factor + epsilon)
    assert color_image.shape[1] * (barcode.rescale_frame_factor - epsilon) < resize_frame.shape[1] < \
           color_image.shape[1] * (barcode.rescale_frame_factor + epsilon)

# Third-party modules
import pytest
import os
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
    return BarcodeClasses.Barcode(color_metric="Average", frame_type="Whole_frame")


def get_template_color_barcode():
    return BarcodeClasses.ColorBarcode(color_metric="Average", frame_type="Whole_frame",
                                       barcode_type="Color")


def get_template_brightness_barcode():
    return BarcodeClasses.BrightnessBarcode(color_metric="Average", frame_type="Whole_frame",
                                            barcode_type="Brightness")


def test_foreback_segmentation(get_test_color_image):
    color_image = get_test_color_image
    fore, back = BarcodeClasses.foreback_segmentation(color_image)
    assert fore.size + back.size == color_image.size
    assert fore.shape[-1] == back.shape[-1] == color_image.shape[-1]


def test_Barcode():
    barcode = BarcodeClasses.Barcode(color_metric="Average", frame_type="Whole_frame", sampled_frame_rate=2,
                                     skip_over=10, total_frames=100, barcode_type="Color")
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
    barcode.enable_save_frames(sampled_rate=-1)
    barcode.read_video("tests/test_data/test_color_video.mp4")
    assert barcode.total_frames == barcode.film_length_in_frames - barcode.skip_over
    assert barcode.high_bound_hor != 0
    assert barcode.low_bound_ver != 0
    assert barcode.saved_frames_sampled_rate > 0


def test_find_film_letter_box():
    barcode = get_template_barcode()
    barcode.read_video("tests/test_data/test_color_video.mp4")
    barcode.find_film_letterbox()
    assert barcode.low_bound_hor >= 0
    assert barcode.high_bound_hor != 0
    assert barcode.low_bound_ver >= 0
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
    barcode.enable_rescale_frames_in_generation(rescale_factor=0.6)
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


def test_get_color_from_frame(get_test_color_image):
    color_frame = get_test_color_image
    barcode = get_template_barcode()

    barcode.color_metric = "Average"
    color = barcode.get_color_from_frame(color_frame)
    assert color.shape == (3,)

    barcode.color_metric = "Median"
    color = barcode.get_color_from_frame(color_frame)
    assert color.shape == (3,)

    barcode.color_metric = "Mode"
    color = barcode.get_color_from_frame(color_frame)
    assert color.shape == (3,)

    barcode.color_metric = "Top-dominant"
    color = barcode.get_color_from_frame(color_frame)
    assert color.shape == (3,)

    barcode.color_metric = "Weighted-dominant"
    color = barcode.get_color_from_frame(color_frame)
    assert color.shape == (3,)

    barcode.color_metric = "Brightest"
    color = barcode.get_color_from_frame(color_frame)
    assert color.shape == (3,)

    barcode.color_metric = "Bright"
    color = barcode.get_color_from_frame(color_frame)
    assert color.shape == (3,)


def test_get_barcode():
    color_barcode = get_template_color_barcode()
    num_rgb = 300
    color_barcode.colors = np.arange(num_rgb).reshape(-1, 3)

    color_barcode_image = color_barcode.get_barcode()
    assert color_barcode_image.shape == (num_rgb / 3, 1, 3)

    color_barcode.reshape_barcode(50)
    color_barcode_image = color_barcode.get_barcode()
    assert color_barcode_image.shape == (50, num_rgb // 3 // 50, 3)

    color_barcode.reshape_barcode(30)
    color_barcode_image = color_barcode.get_barcode()
    assert color_barcode_image.shape == (30, num_rgb // 3 // 30, 3)

    brightness_barcode = get_template_brightness_barcode()
    num_brightness = 100
    brightness_barcode.brightness = np.arange(num_brightness).reshape(-1, 1)
    brightness_barcode_image = brightness_barcode.get_barcode()
    assert brightness_barcode_image.shape == (num_brightness, 1)

    brightness_barcode.reshape_barcode(50)
    brightness_barcode_image = brightness_barcode.get_barcode()
    assert brightness_barcode_image.shape == (50, num_brightness // 50)

    brightness_barcode.reshape_barcode(30)
    brightness_barcode_image = brightness_barcode.get_barcode()
    assert brightness_barcode_image.shape == (30, num_brightness // 30)


def test_set_letterbox_bound():
    barcode = get_template_barcode()
    barcode.set_letterbox_bound(10, 300, 20, 720)
    assert barcode.user_defined_letterbox == True
    assert barcode.low_bound_ver == 10
    assert barcode.high_bound_ver == 300
    assert barcode.low_bound_hor == 20
    assert barcode.high_bound_hor == 720


def test_automatic_find_letterbox():
    barcode = get_template_barcode()
    barcode.read_video("tests/test_data/test_color_video.mp4")
    barcode.automatic_find_letterbox()
    assert barcode.low_bound_hor >= 0
    assert barcode.high_bound_hor != 0
    assert barcode.low_bound_ver >= 0
    assert barcode.high_bound_ver != 0


def test_add_meta_data():
    barcode = get_template_barcode()
    barcode.meta_data = None
    barcode.add_meta_data("Film Title", "Mission: Impossible")
    assert barcode.meta_data is not None
    assert barcode.meta_data["Film Title"] == "Mission: Impossible"


def test_save_as_json():
    color_barcode = get_template_color_barcode()
    color_barcode.colors = np.arange(300).reshape(-1, 3)
    color_barcode.save_as_json()

    expected_filename = "saved_{:s}_barcode_{:s}_{:s}.json".format(color_barcode.barcode_type,
                                                                   color_barcode.frame_type,
                                                                   color_barcode.color_metric)

    assert os.path.exists(expected_filename)
    os.remove(expected_filename)

    brightness_barcode = get_template_brightness_barcode()
    brightness_barcode.brightness = np.arange(100).reshape(-1, 1)
    brightness_barcode.enable_save_frames()
    brightness_barcode.saved_frames = np.array([None])
    brightness_barcode.save_as_json()

    expected_filename = "saved_{:s}_barcode_{:s}_{:s}.json".format(brightness_barcode.barcode_type,
                                                                   brightness_barcode.frame_type,
                                                                   brightness_barcode.color_metric)

    assert os.path.exists(expected_filename)
    os.remove(expected_filename)


def test_collect_color_color_barcode():
    color_barcode = get_template_color_barcode()
    color_barcode.skip_over = 0
    color_barcode.sampled_frame_rate = 1
    color_barcode.total_frames = 50
    color_barcode.enable_save_frames(sampled_rate=0.1)
    color_barcode.collect_colors("tests/test_data/test_color_video.mp4")
    assert color_barcode.colors.shape == (50, 3)
    assert color_barcode.saved_frames is not None
    assert len(color_barcode.saved_frames) > 0


def test_collect_color_multi_thread_color_barcode():
    color_barcode = get_template_color_barcode()
    color_barcode.skip_over = 0
    color_barcode.sampled_frame_rate = 1
    color_barcode.total_frames = 100
    color_barcode.enable_save_frames(sampled_rate=0.1)
    color_barcode.multi_thread_collect_colors("tests/test_data/test_color_video.mp4", num_thread=2)

    assert color_barcode.colors.shape == (100, 3)
    assert color_barcode.saved_frames is not None
    assert len(color_barcode.saved_frames) > 0


def test_collect_brightness_brightness_barcode():
    brightness_barcode = get_template_brightness_barcode()
    brightness_barcode.color_metric = "Average"
    brightness_barcode.skip_over = 0
    brightness_barcode.sampled_frame_rate = 1
    brightness_barcode.total_frames = 50
    brightness_barcode.enable_save_frames(sampled_rate=0.1)
    brightness_barcode.collect_brightness("tests/test_data/test_color_video.mp4")

    assert brightness_barcode.brightness.shape == (50, 1)
    assert brightness_barcode.saved_frames is not None
    assert len(brightness_barcode.saved_frames) > 0

    brightness_barcode = get_template_brightness_barcode()
    brightness_barcode.color_metric = "Brightest"
    brightness_barcode.skip_over = 0
    brightness_barcode.sampled_frame_rate = 1
    brightness_barcode.total_frames = 50
    brightness_barcode.enable_save_frames(sampled_rate=0.1)
    brightness_barcode.collect_brightness("tests/test_data/test_color_video.mp4")

    assert brightness_barcode.brightness.shape == (50,)
    assert brightness_barcode.saved_frames is not None
    assert len(brightness_barcode.saved_frames) > 0


def test_collect_brightness_multi_thread_brightness_barcode():
    brightness_barcode = get_template_brightness_barcode()
    brightness_barcode.color_metric = "Average"
    brightness_barcode.skip_over = 0
    brightness_barcode.sampled_frame_rate = 1
    brightness_barcode.total_frames = 100
    brightness_barcode.enable_save_frames(sampled_rate=0.1)
    brightness_barcode.multi_thread_collect_brightness("tests/test_data/test_color_video.mp4", num_thread=2)

    assert brightness_barcode.brightness.shape == (100, 1)
    assert brightness_barcode.saved_frames is not None
    assert len(brightness_barcode.saved_frames) > 0

    brightness_barcode = get_template_brightness_barcode()
    brightness_barcode.color_metric = "Brightest"
    brightness_barcode.skip_over = 0
    brightness_barcode.sampled_frame_rate = 1
    brightness_barcode.total_frames = 100
    brightness_barcode.enable_save_frames(sampled_rate=0.1)
    brightness_barcode.multi_thread_collect_brightness("tests/test_data/test_color_video.mp4", num_thread=2)

    assert brightness_barcode.brightness.shape == (100,)
    assert brightness_barcode.saved_frames is not None
    assert len(brightness_barcode.saved_frames) > 0

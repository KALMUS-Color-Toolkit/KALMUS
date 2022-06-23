# Third-party modules
import pytest
import matplotlib.pyplot as plt

# kalmus module being tested
import kalmus.tkinter_windows.gui_utils as gui_utils
from kalmus.barcodes.BarcodeGenerator import build_barcode_from_json


def get_color_barcode():
    return build_barcode_from_json("tests/test_data/i_robot_Median_Whole_frame_Color.json",
                                   barcode_type="Color")


def get_brightness_barcode():
    return build_barcode_from_json("tests/test_data/i_robot_Average_Whole_frame_Brightness.json",
                                    barcode_type="Brightness")


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_compare_two_barcodes():
    color_barcode_1 = get_color_barcode()
    color_barcode_2 = get_color_barcode()
    color_barcode_1.colors = color_barcode_1.colors[:8000]
    color_barcode_1.barcode = None
    color_barcode_2.colors = color_barcode_2.colors[:6000]
    color_barcode_2.barcode = None

    result_text = gui_utils.get_comparison_result_text(color_barcode_1, color_barcode_2)
    assert "NRMSE Similarity" in result_text
    assert "SSIM Similarity" in result_text
    assert "Cross Correlation" in result_text
    assert "Local Cross Correlation" in result_text
    assert "Needleman Wunsch Similarity" in result_text
    assert "Smith Waterman Similarity" in result_text

    result_text = gui_utils.get_comparison_result_text(color_barcode_1, color_barcode_1)
    assert "NRMSE Similarity" in result_text
    assert "SSIM Similarity" in result_text
    assert "Cross Correlation" in result_text
    assert "Local Cross Correlation" in result_text
    assert "Needleman Wunsch Similarity" in result_text
    assert "Smith Waterman Similarity" in result_text

    brightness_barcode_1 = get_brightness_barcode()
    brightness_barcode_2 = get_brightness_barcode()
    brightness_barcode_1.brightness = brightness_barcode_1.brightness[:8000]
    brightness_barcode_1.barcode = None
    brightness_barcode_2.brightness = brightness_barcode_2.brightness[:6000]
    brightness_barcode_2.barcode = None

    result_text = gui_utils.get_comparison_result_text(brightness_barcode_1, brightness_barcode_2)
    assert "NRMSE Similarity" in result_text
    assert "SSIM Similarity" in result_text
    assert "Cross Correlation" in result_text
    assert "Local Cross Correlation" in result_text
    assert "Needleman Wunsch Similarity" in result_text
    assert "Smith Waterman Similarity" in result_text

    result_text = gui_utils.get_comparison_result_text(brightness_barcode_1, brightness_barcode_1)
    assert "NRMSE Similarity" in result_text
    assert "SSIM Similarity" in result_text
    assert "Cross Correlation" in result_text
    assert "Local Cross Correlation" in result_text
    assert "Needleman Wunsch Similarity" in result_text
    assert "Smith Waterman Similarity" in result_text

    result_text = gui_utils.get_comparison_result_text(color_barcode_1, brightness_barcode_1)
    assert "ERROR" in result_text


def test_get_time():
    color_barcode = get_color_barcode()
    brightness_barcode = get_brightness_barcode()

    frame, hr, min, sec = gui_utils.get_time(color_barcode, 40, 100)

    assert int(frame) == 13000
    assert int(hr) == 0
    assert int(min) == 7
    assert int(sec) == 13

    frame, hr, min, sec = gui_utils.get_time(brightness_barcode, 40, 100)

    assert int(frame) == 13000
    assert int(hr) == 0
    assert int(min) == 7
    assert int(sec) == 13


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_graph():
    # Turn off the interactive mode of matplotlib
    plt.ioff()
    color_barcode = get_color_barcode()
    brightness_barcode = get_brightness_barcode()

    fig, ax = plt.subplots(2, 2)

    gui_utils.update_graph(color_barcode, color_barcode, ax)

    main_title = "    Frame Type:{:s}    {:s} Metric:{:s}".format(color_barcode.frame_type, color_barcode.barcode_type,
                                                                  color_barcode.color_metric)

    assert main_title in ax[0][0].get_title()
    assert main_title in ax[1][0].get_title()
    assert ax[0][1].get_ylabel() == "Number of frames"
    assert ax[1][1].get_xlabel() == "Color Hue (0 - 360)"

    gui_utils.update_graph(brightness_barcode, brightness_barcode, ax)

    main_title = "    Frame Type:{:s}    {:s} Metric:{:s}".format(brightness_barcode.frame_type,
                                                                  brightness_barcode.barcode_type,
                                                                  brightness_barcode.color_metric)

    assert ax[0][0].get_title() == "Barcode 1" + main_title
    assert ax[1][0].get_title() == "Barcode 2" + main_title
    assert ax[0][1].get_ylabel() == "Number of frames"
    assert ax[1][1].get_xlabel() == "Brightness (0 - 255)"


def test_resource_path():
    path = gui_utils.resource_path("kalmus_icon.ico")
    assert "../data" in path
    assert "kalmus_icon" in path

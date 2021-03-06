# Third-party modules
import pytest

# kalmus module being tested
import kalmus.barcodes.BarcodeGenerator as Generator


def get_template_generator():
    return Generator.BarcodeGenerator(frame_type="Whole_frame", color_metric="Average",
                                      barcode_type="Color", skip_over=0, sampled_frame_rate=1,
                                      total_frames=10)


def test_build_barcode_from_json():
    barcode = Generator.build_barcode_from_json("tests/test_data/i_robot_Median_Whole_frame_Color.json",
                                                barcode_type="Color")
    assert isinstance(barcode, Generator.ColorBarcode)
    assert barcode.barcode_type == "Color"
    assert barcode.meta_data is not None
    assert barcode.colors.shape[0] > 0
    assert barcode.colors.shape[1] == 3

    barcode = Generator.build_barcode_from_json("tests/test_data/i_robot_Average_Whole_frame_Brightness.json",
                                                barcode_type="Brightness")
    assert isinstance(barcode, Generator.BrightnessBarcode)
    assert barcode.barcode_type == "Brightness"
    assert barcode.saved_frames is not None
    assert len(barcode.saved_frames) > 0
    assert barcode.brightness.shape[0] > 0
    assert barcode.brightness.shape[1] == 1


def test_BarcodeGenerator():
    generator = Generator.BarcodeGenerator(frame_type="Foreground", color_metric="Top-dominant",
                                           barcode_type="Color", skip_over=0, sampled_frame_rate=2,
                                           total_frames=100)

    assert generator.frame_type == "Foreground"
    assert generator.color_metric == "Top-dominant"
    assert generator.barcode_type == "Color"
    assert generator.skip_over == 0
    assert generator.sampled_frame_rate == 2
    assert generator.total_frames == 100
    assert generator.barcode is None


def test_generate_barcode():
    generator = get_template_generator()
    generator.total_frames = 50
    generator.generate_barcode(video_file_path="tests/test_data/test_color_video.mp4",
                               user_defined_letterbox=True, low_ver=200, high_ver=0, left_hor=0, right_hor=100,
                               num_thread=2, save_frames=True, save_frames_rate=0.1, rescale_frames_factor=0.64)
    barcode = generator.get_barcode()
    assert isinstance(barcode, Generator.ColorBarcode)

    assert barcode.colors.shape[0] > 0
    assert barcode.colors.shape[1] == 3

    assert barcode.total_frames == 50
    assert len(barcode.saved_frames) > 0

    assert barcode.low_bound_ver == 0
    assert barcode.high_bound_ver == 200
    assert barcode.low_bound_hor == 0
    assert barcode.high_bound_hor == 100

    generator.generate_barcode(video_file_path="tests/test_data/test_color_video.mp4")
    barcode = generator.get_barcode()
    assert isinstance(barcode, Generator.ColorBarcode)

    assert barcode.colors.shape[0] > 0
    assert barcode.colors.shape[1] == 3

    assert barcode.total_frames == 50

    generator.barcode_type = "Brightness"
    generator.total_frames = 20
    generator.generate_barcode(video_file_path="tests/test_data/test_color_video.mp4", num_thread=2)
    barcode = generator.get_barcode()
    assert isinstance(barcode, Generator.BrightnessBarcode)
    assert barcode.brightness.shape[0] == 20
    assert barcode.brightness.shape[1] == 1

    generator.generate_barcode(video_file_path="tests/test_data/test_color_video.mp4")
    barcode = generator.get_barcode()
    assert isinstance(barcode, Generator.BrightnessBarcode)
    assert barcode.brightness.shape[0] == 20
    assert barcode.brightness.shape[1] == 1


def test_generate_barcode_from_json():
    generator = get_template_generator()
    generator.barcode_type = "Color"
    generator.generate_barcode_from_json("tests/test_data/i_robot_Median_Whole_frame_Color.json")

    barcode = generator.get_barcode()
    assert isinstance(barcode, Generator.ColorBarcode)
    assert barcode.frame_type == "Whole_frame"
    assert barcode.color_metric == "Median"
    assert barcode.colors.shape[0] > 0
    assert barcode.colors.shape[1] == 3

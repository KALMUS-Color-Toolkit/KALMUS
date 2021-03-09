# Third-party modules
import pytest
import os

# kalmus module being tested
import kalmus.command_line_generator as cli


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_cli_generator_main():
    mock_sys_args_array = ['-p', 'tests/test_data/test_color_video.mp4',
                           '--frame_type', 'Low_contrast_region',
                           '--color_metric', 'Median',
                           '--barcode_type', 'Brightness',
                           '--step', '2',
                           '--skip', '10',
                           '--total_frames', '50',
                           '--num_thread', '2',
                           '--saved_frame_rate', '0.5',
                           '--rescale_frame_factor', '0.25',
                           '-o', './test_barcode_cli.json']

    cli.main(mock_sys_args_array)
    assert os.path.exists('test_barcode_cli.json')
    os.remove('test_barcode_cli.json')

    mock_sys_args_array_no_saved_frame = ['-p', 'tests/test_data/test_color_video.mp4',
                                          '--frame_type', 'Low_contrast_region',
                                          '--color_metric', 'Median',
                                          '--barcode_type', 'Brightness',
                                          '--step', '2',
                                          '--skip', '10',
                                          '--total_frames', '50',
                                          '--num_thread', '2',
                                          '--rescale_frame_factor', '0.25',
                                          '-o', './test_barcode_cli_with_no_frame_saved.json']
    cli.main(mock_sys_args_array_no_saved_frame)
    assert os.path.exists('test_barcode_cli_with_no_frame_saved.json')
    os.remove('test_barcode_cli_with_no_frame_saved.json')

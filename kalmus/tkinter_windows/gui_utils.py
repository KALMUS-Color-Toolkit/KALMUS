""" KALMUS tkinter GUI utility """

import cv2
import kalmus.utils.measure_utils as measure_utils
import os
import sys
import numpy as np
from skimage.color import hsv2rgb, rgb2hsv

from matplotlib.ticker import FuncFormatter


def compare_two_barcodes(barcode_1, barcode_2):
    """
    Compare the similarity between two barcodes using NRMSE, SSIM, cross correlation, local cross correlation,
    Needleman Wunsch, and Smith Waterman alignment matching

    :param barcode_1: The input barcode 1
    :param barcode_2: The input barcode 2
    :return: The simiarity scores computed using all six metrics
    """
    # Resize two barcodes so they have the same shape
    # Alway resize the small barcode to the shape of the larger barcode
    target_barcode_1 = barcode_1.get_barcode().astype("float64")
    target_barcode_2 = barcode_2.get_barcode().astype("float64")
    if target_barcode_1.size <= target_barcode_2.size:
        target_barcode_1 = cv2.resize(target_barcode_1, dsize=target_barcode_2.shape[:2][::-1],
                                      interpolation=cv2.INTER_LINEAR)
    elif target_barcode_1.size > target_barcode_2.size:
        target_barcode_2 = cv2.resize(target_barcode_2, dsize=target_barcode_1.shape[:2][::-1],
                                      interpolation=cv2.INTER_LINEAR)

    # Get the cross correlation and local cross correlation
    cross_corre = measure_utils.cross_correlation(target_barcode_1.astype("float64"),
                                                  target_barcode_2.astype("float64"))
    loc_cross_corre = measure_utils.local_cross_correlation(target_barcode_1.astype("float64"),
                                                            target_barcode_2.astype("float64"))

    # Get the Normalized root mean squared error and and Structual similarity index measurement
    nrmse = measure_utils.nrmse_similarity(target_barcode_1.astype("float64"),
                                           target_barcode_2.astype("float64"))
    ssim = measure_utils.ssim_similarity(target_barcode_1.astype("float64"),
                                         target_barcode_2.astype("float64"))

    # Get the color/brightness of two barcodes
    if barcode_1.barcode_type == "Color":
        colors_barcode_1 = barcode_1.colors
        colors_barcode_2 = barcode_2.colors
    else:
        colors_barcode_1 = barcode_1.brightness
        colors_barcode_2 = barcode_2.brightness

    # Resample the barcodes if the barcodes have different size/length
    if colors_barcode_1.shape[0] > colors_barcode_2.shape[0]:
        colors_barcode_1 = colors_barcode_1[measure_utils.get_resample_index(len(colors_barcode_1),
                                                                             len(colors_barcode_2))]
    elif colors_barcode_1.shape[0] < colors_barcode_2.shape[0]:
        colors_barcode_2 = colors_barcode_2[measure_utils.get_resample_index(len(colors_barcode_2),
                                                                             len(colors_barcode_1))]
    # Convert the barcode to character string for alignment matching comparison
    # Convert the barcode to correct character based on its barcode type
    if barcode_1.barcode_type == "Color":
        string_1 = measure_utils.generate_hue_strings_from_color_barcode(colors_barcode_1)
        string_2 = measure_utils.generate_hue_strings_from_color_barcode(colors_barcode_2)
    else:
        string_1 = measure_utils.generate_brightness_string_from_brightness_barcode(colors_barcode_1)
        string_2 = measure_utils.generate_brightness_string_from_brightness_barcode(colors_barcode_2)

    # Get the Needleman Wunsch and Smith Waterman alignment matching score
    needleman = measure_utils.compare_needleman_wunsch(string_1, string_2, normalized=True)
    smithw = measure_utils.compare_smith_waterman(string_1, string_2, normalized=True)

    return cross_corre, loc_cross_corre, nrmse, ssim, needleman, smithw


def get_comparison_result_text(barcode_1, barcode_2):
    """
    Get the text comparison result using the compare_two_barcodes function

    :param barcode_1: The compared barcode 1
    :param barcode_2: The compared barcode 2
    :return: The text comparison result
    """
    # Return error text if two barcodes are not in the same type
    if barcode_1.barcode_type != barcode_2.barcode_type:
        result_text = "ERROR:\nComparison between different types of\n" \
                      "barcode type {:s} and {:s}\nare not allowed.".format(barcode_1.barcode_type,
                                                                            barcode_2.barcode_type)
        return result_text

    # Get the similarity score from the compare_two_barcodes function
    cross_corre, loc_cross_corre, nrmse, ssim, needleman, smith = compare_two_barcodes(barcode_1, barcode_2)

    # Get the text result
    result_text = "Comparison metrics:\n" \
                  "NRMSE Similarity:                  {:10.4f}\n" \
                  "SSIM Similarity:                     {:10.4f}\n" \
                  "Cross Correlation:                 {:10.4f}\n" \
                  "Local Cross Correlation:         {:10.4f}\n" \
                  "Needleman Wunsch Similarity:{:10.4f}\n" \
                  "Smith Waterman Similarity:     {:10.4f}".format(nrmse, ssim, cross_corre, loc_cross_corre,
                                                                   needleman, smith)
    return result_text


def update_graph(barcode_1, barcode_2, axes, bin_step=5):
    """
    Update the plotted graph (in place)

    :param barcode_1: The barcode 1
    :param barcode_2: The barcode 2
    :param axes: The axes of the plotted figure
    :param bin_step: The step of histogram bin
    """
    # Plot the barcode with the correct color map based on their barcode types
    if barcode_1.barcode_type == "Brightness":
        axes[0][0].imshow(barcode_1.get_barcode().astype("uint8"), cmap='gray', vmin=0, vmax=255)
    else:
        axes[0][0].imshow(barcode_1.get_barcode().astype("uint8"))

    if barcode_2.barcode_type == "Brightness":
        axes[1][0].imshow(barcode_2.get_barcode().astype("uint8"), cmap='gray', vmin=0, vmax=255)
    else:
        axes[1][0].imshow(barcode_2.get_barcode().astype("uint8"))

    # Rescale the axis range
    # And update the plot
    for axis in axes.ravel():
        axis.relim()
        axis.autoscale_view()

    # Update the axis ticks of the plotted axes
    update_axes_ticks(barcode_1, barcode_2, axes)

    # Update the title of the plotted axes
    update_axes_title(axes, barcode_1, barcode_2)

    # Update the histogram of the barcode 1
    update_hist(barcode_1, ax=axes[0][1], bin_step=bin_step)

    # Update the histogram of the barcode 2
    update_hist(barcode_2, ax=axes[1][1], bin_step=bin_step)


def update_axes_ticks(barcode1, barcode2, axes):
    """
    Update the axes ticks
    If two barcodes have the same temporal dimensions, the ticks will show the temporal position of a pixel in the
    barcode image. Otherwise, the axes ticks will show the spatial position of a pixel.

    :param barcode1: The barcode 1
    :param barcode2: The barcode 2
    :param axes: The axes of the plotted figure
    """
    frames_per_column_1 = barcode1.sampled_frame_rate * barcode1.get_barcode().shape[0] \
                          * barcode1.scale_factor

    frames_per_column_2 = barcode2.sampled_frame_rate * barcode2.get_barcode().shape[0] \
                          * barcode2.scale_factor

    seconds_per_column1 = frames_per_column_1 / barcode1.fps
    seconds_per_column2 = frames_per_column_2 / barcode2.fps

    axes[0][0].set_ylabel("{:.2f}s per column".format(seconds_per_column1))
    axes[1][0].set_ylabel("{:.2f}s per column".format(seconds_per_column2))

    if np.round(seconds_per_column1, decimals=0) == np.round(seconds_per_column2, decimals=0):
        def get_seconds_str_yticks(tick_value, pos):
            seconds = np.round(tick_value * seconds_per_column2, decimals=0).astype("int")
            return "{:02d}:{:02d}".format(seconds // 60, seconds % 60)

        axes[1][0].xaxis.set_major_formatter(FuncFormatter(get_seconds_str_yticks))
        axes[1][0].set_xlabel("Elapsed Time (mins:secs)")

        def get_seconds_str_xticks(tick_value, pos):
            seconds = tick_value * barcode1.sampled_frame_rate * barcode1.scale_factor / barcode1.fps
            return "{:.1f}s".format(seconds)

        axes[0][0].yaxis.set_major_formatter(FuncFormatter(get_seconds_str_xticks))
        axes[1][0].yaxis.set_major_formatter(FuncFormatter(get_seconds_str_xticks))


def update_axes_title(axes, barcode_1, barcode_2):
    """
    Update the title of the plotted axes (in place)

    :param axes: The plotted axes of the figure
    :param barcode_1: The barcode 1
    :param barcode_2: The barcode 2
    """
    title_1 = "Barcode 1"
    title_2 = "Barcode 2"

    keys = ["Film Title", "Produced Year", "Genre"]

    # Update the meta data into the title of the plotted figure
    if barcode_1.meta_data is not None:
        for key in keys:
            if key in barcode_1.meta_data.keys():
                title_1 += "    {:s}: {:s}".format(key, barcode_1.meta_data[key])

    # Update the Frame sampling type and color/brightness metric into the title
    title_1 += "    Frame Type:{:s}    {:s} Metric:{:s}".format(barcode_1.frame_type, barcode_1.barcode_type,
                                                                barcode_1.color_metric)

    # Update the meta data into the title of the plotted figure
    if barcode_2.meta_data is not None:
        for key in keys:
            if key in barcode_2.meta_data.keys():
                title_2 += "    {:s}: {:s}".format(key, barcode_2.meta_data[key])

    # Update the Frame sampling type and color/brightness metric into the title
    title_2 += "    Frame Type:{:s}    {:s} Metric:{:s}".format(barcode_2.frame_type, barcode_2.barcode_type,
                                                                barcode_2.color_metric)

    # Set up the title
    axes[0][0].set_title(title_1, fontsize=8)
    axes[1][0].set_title(title_2, fontsize=8)

    # Change the histogram's label and xticks accordingly
    if barcode_1.barcode_type == "Color":
        axes[0][1].set_xticks(np.arange(0, 361, 30))
        axes[0][1].set_xlabel("Color Hue (0 - 360)")
        axes[0][1].set_ylabel("Number of frames")
    elif barcode_1.barcode_type == "Brightness":
        axes[0][1].set_xticks(np.arange(0, 256, 16))
        axes[0][1].set_xlabel("Brightness (0 - 255)")
        axes[0][1].set_ylabel("Number of frames")

    if barcode_2.barcode_type == "Color":
        axes[1][1].set_xticks(np.arange(0, 361, 30))
        axes[1][1].set_xlabel("Color Hue (0 - 360)")
        axes[1][1].set_ylabel("Number of frames")
    elif barcode_2.barcode_type == "Brightness":
        axes[1][1].set_xticks(np.arange(0, 256, 32))
        axes[1][1].set_xlabel("Brightness (0 - 255)")
        axes[1][1].set_ylabel("Number of frames")


def update_hist(barcode, ax, bin_step=5):
    """
    Update the histogram of the plotted figure (in place)

    :param barcode: The barcode of the corresponding histogram
    :param ax: The axis that contain the histogram
    :param bin_step: The step of the bin in the plotted histogram
    """
    bin_step = bin_step

    # Plot the histogram based on the barcode's type
    if barcode.barcode_type == "Color":
        # If the barcode type is color
        # Then plot the barcode's hue value
        normalized_barcode = barcode.get_barcode().astype("float") / 255

        hsv_colors = rgb2hsv(normalized_barcode.reshape(-1, 1, 3))
        hue = hsv_colors[..., 0] * 360

        N, bins, patches = ax.hist(hue[:, 0], bins=(np.arange(0, 361, bin_step)))

        # Paint each bin with its corresponding color in hue
        paint_hue_hist(bin_step, patches)
    else:
        # If the barcode type is brightness
        N, bins, patches = ax.hist(barcode.brightness[:, 0], bins=(np.arange(0, 256, bin_step)))

        # Then paint each bin with its brightness intensity
        paint_gray_hist(bin_step, patches, opacity=0.9)


def paint_hue_hist(bin_step, patches):
    """
    Paint each bin of the hue histogram with its corresponding color in hue (in place)

    :param bin_step: The step of the bin in the histogram
    :param patches: The patches of the histogram that will be painted later
    """
    # Paint each bin of the histogram
    for i in range(len(patches)):
        # Get the hue first
        hue = np.array([i * bin_step / 360.0, 1.0, 1.0]).astype("float64")
        hue = np.expand_dims(np.expand_dims(hue, 0), 0)

        # Then get the corresponding color
        rgb = hsv2rgb(hue).tolist()
        rgb_tuple = (rgb[0][0][0], rgb[0][0][1], rgb[0][0][2])

        # Paint each patch of the histogram
        patches[i].set_facecolor(rgb_tuple)


def paint_gray_hist(bin_step, patches, opacity=0.8):
    """
    Paint each bin of the brightness histogram with its corresponding brightness intensity (in place)

    :param bin_step: The step of the bin in the histogram
    :param patches: The patches of the histogram
    :param opacity: Opacity of the brightness intensity to avoid totally white in the high intensity bin \
                    To make the histogram bin in high intensity area more observable
    """
    for i in range(len(patches)):
        # Get the RGB gray color for each bin
        bri_rgb_tuple = (bin_step * i * opacity / 255, bin_step * i * opacity / 255, bin_step * i * opacity / 255)
        patches[i].set_facecolor(bri_rgb_tuple)


def resource_path(relative_path):
    """
    Internal utility function
    Use to convert the input relative path to the absolute path
    This is used for the Pyinstaller wrapper

    :param relative_path: The relative path to the file
    :return: The absolute path to the file
    """
    try:
        # If the MEIPASS base path exist
        base_path = sys._MEIPASS
    except Exception:
        # Otherwise use the absolute path
        if relative_path.endswith(".ico"):
            # If the path points to .ico image
            if os.name != "nt":
                # If the running os is linux
                relative_path = relative_path[:-3]
                # Replace the .ico image with image in .xbm format
                relative_path += "xbm"

        # Join the path
        base_path = os.path.abspath(os.path.dirname(__file__))
        base_path = os.path.join(base_path, '../data')

        if relative_path.endswith(".xbm"):
            # If the image is .xbm image
            if os.name != "nt":
                # and the running os is linux
                # Add @ identifier at the front of path
                base_path = "@" + base_path

    # Return the path
    return os.path.join(base_path, relative_path)

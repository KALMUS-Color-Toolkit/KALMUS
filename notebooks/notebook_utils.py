import matplotlib.pyplot as plt
import numpy as np

import kalmus.utils.artist as artist
import kalmus.utils.visualization_utils as vis
from kalmus.barcodes.BarcodeGenerator import BarcodeGenerator, frame_types


def show_image_with_color(image, color_metric="Average", frame_type="Whole_frame",
                          color_image_width=None, add_separate_line=False, separate_line_width=3,
                          ax=None, figsize=(6, 4), title=None, axis_off=False):
    """
    Helper function that show the extracted image using specified frame_type along with color measured using
    specified color_metric

    :param image: Numpy.ndarray Expected image shape == (height, width, channels=3)
    :param color_metric: The metric used to measure the color of region of interest in image. \
                         see kalmus.barcodes.BarcodeGenerator.color_metrics for more references
    :param frame_type: The type of region that is interested in the image. \
                       see kalmus.barcodes.BarcodeGenerator.frame_type for more references
    :param color_image_width: The width of color plotted on the right side of image. \
                              By default color_image_width=None, the color image width will be 0.15 \
                              of input image's width.
    :param add_separate_line: Whether add a white separation line between image and color image
    :param separate_line_width: Width of the separation line in pixels
    :param ax: If the Axes object is given, plot on the given Axes instead
    :param figsize: The size of the plotted figure
    :param title: The title of the plot, by default title="{:color_metric} Color using {:frame_type}"
    :param axis_off: Whether turn the plot's axis off or not. By default, axis is on.
    """
    helper_generator = BarcodeGenerator(color_metric=color_metric, frame_type=frame_type)
    helper_generator.instantiate_barcode_object()
    helper_barcode = helper_generator.get_barcode()

    low_bound_ver, high_bound_ver, low_bound_hor, high_bound_hor = artist.get_letter_box_from_frames(image)

    helper_barcode.enable_user_defined_letterbox()
    helper_barcode.low_bound_ver = low_bound_ver
    helper_barcode.high_bound_ver = high_bound_ver
    helper_barcode.low_bound_hor = low_bound_hor
    helper_barcode.high_bound_hor = high_bound_hor

    sampled_frame = helper_barcode.process_frame(image)
    if len(sampled_frame.shape) <= 2:
        sampled_frame = sampled_frame.reshape(-1, 1, 3)
    color = helper_barcode.get_color_from_frame(sampled_frame)

    cropped_frame = helper_barcode.remove_letter_box_from_frame(image)
    if frame_type in frame_types[3:5]:
        fore, back = artist.grabcut_foreback_segmentation(image=cropped_frame, return_masks=True)
        if frame_type == "Foreground":
            labeled_image = np.zeros(shape=fore.shape)
            labeled_image[fore] = 1
        else:
            labeled_image = np.zeros(shape=back.shape)
            labeled_image[back] = 1
        extracted_region = vis.extract_region_with_index(cropped_frame, 1, labeled_image)
    elif frame_type in frame_types[1:3]:
        if frame_type == "Low_contrast_region":
            extracted_region = vis.show_low_contrast_region(cropped_frame, return_region_image=True)
        else:
            extracted_region = vis.show_high_contrast_region(cropped_frame, return_region_image=True)
    else:
        extracted_region = cropped_frame

    if color_image_width is None:
        color_image_width = int(0.15 * extracted_region.shape[1])
    color_image = np.ones(shape=(extracted_region.shape[0], color_image_width, 3))
    color = color.reshape(3,)
    color_image *= color

    if add_separate_line:
        line = np.ones(shape=(extracted_region.shape[0], separate_line_width, 3))
        line *= 255
        color_image = np.concatenate([line, color_image], axis=1)

    concat_img = np.concatenate([extracted_region, color_image], axis=1).clip(0, 255).astype("uint8")

    if title is None:
        title = "{:s} Color using {:s}".format(color_metric, frame_type.replace("_", " "))

    if ax is not None:
        ax.imshow(concat_img)
        ax.set_title(title)
        if axis_off:
            ax.axis("off")
    else:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        ax.imshow(concat_img)
        ax.set_title(title)
        if axis_off:
            ax.axis("off")
        plt.show()


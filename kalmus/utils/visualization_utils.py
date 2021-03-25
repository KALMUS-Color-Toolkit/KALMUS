""" Visualization Utility """

import numpy as np
import matplotlib.pyplot as plt
from kalmus.utils.artist import get_contrast_matrix_and_labeled_image


def show_color(color, figure_size=(9, 6), title="",
               axis_off=False, save_image=False, file_name="test.png", return_color=False):
    """
    Plot the rgb color.

    :param color: 1D array contains the R, G, and B channel values
    :type color: numpy.ndarray
    :param figure_size: Size of the plotted figure
    :type figure_size: tuple
    :param title: The title of the plotted color
    :type title: str
    :param axis_off: True to set the axis of the plot figure off. False to have the axis on the side of \
    figure.
    :type axis_off: bool
    :param save_image: True to save the plot figure into the path that user provide. False not to save \
    the plot figure
    :type save_image: bool
    :param file_name: The filename of the saved figure. The default path to the saved image is test.png
    :type file_name: str
    :param return_color: Return the numpy array (shape==30 x 30 x 3) of color block if True. Directly plot the color \
    if False
    :type return_color: bool
    :return: Return the numpy array of color block if return_color is True.
    :rtype: numpy.ndarray
    """
    # Generate a block image where each pixel of this block image is the plotted RGB color
    clr = np.ones(shape=(30, 30, 3), dtype=np.uint8) * np.uint8(color)

    if return_color:
        return clr

    # Set up the figure
    plt.figure(figsize=figure_size)
    plt.imshow(clr)
    plt.title(title)
    # Whether to set the axis off
    if axis_off:
        plt.axis('off')
    # Whether to save the plot figure
    if save_image:
        plt.savefig(file_name)
    plt.show()


def show_colors_in_sequence(colors, figure_size=(9, 6), title="", axis_off=False,
                            save_image=False, file_name="test.png", horizontal=True,
                            return_color_sequence=False):
    """
    Plot a sequence of RGB colors either horizontally or vertically in line

    :param colors: 2D array of RGB colors. Expected sequence shape==Number of colors x channels (3)
    :type colors: numpy.ndarray
    :param figure_size: the size of the plot figure
    :type figure_size: tuple
    :param title: the title of the plot
    :type title: str
    :param axis_off: True to set the axis of the figure off. False to have the axis with the figure
    :type axis_off: bool
    :param save_image: True to save the plot figure. False do not save figure
    :type save_image: bool
    :param file_name: the path of the saved figure
    :type file_name: str
    :param horizontal: True to plot the sequence of colors horizontally, False to plot the sequence of colors \
                       vertically
    :type horizontal: bool
    :param return_color_sequence: Return the numpy array (shape==30 x (30 * num_colors) x 3) of color sequence if True \
                                  Directly plot the color sequence if False
    :type return_color_sequence: bool
    :return: Return the numpy array of the color sequence image if return_color_sequence is True.
    :rtype: numpy.ndarray
    """
    # A chain/sequence of color blocks
    clr_chain = []
    # Size of the color blocks in the display chain/sequence
    block_size = 30
    # Append blocks into the color chain
    for i in range(len(colors)):
        color_block = np.ones(shape=(block_size, block_size, 3), dtype=np.uint8) * np.uint8(colors[i])
        clr_chain.append(color_block)

    clr_chain = np.array(np.concatenate(clr_chain))

    # Now the color chain is vertical. To have horizontal color chain, we transpose the sequence to rotate it
    if horizontal:
        clr_chain = clr_chain.transpose([1, 0, 2])

    if return_color_sequence:
        return clr_chain

    plt.figure(figsize=figure_size)
    plt.imshow(clr_chain)
    plt.title(title)
    if axis_off:
        plt.axis("off")
    if save_image:
        plt.savefig(file_name)
    plt.show()


def show_color_matrix(color_2d_array, mode="truncate", figure_size=(9, 4),
                      title="", axis_off=False,
                      save_image=False, file_name="Block.png", return_matrix=False, return_figure=False):
    """
    Show a matrix of colors (color barcodes). Two modes are available "truncate" and "padding"
    "truncate" mode will truncate the last row of the color matrix if it has different len with respect
    to the other rows. "padding" mode will pad white colors to the last row until the last row has the
    same length as the other rows

    :param color_2d_array: the input color matrix. Expected the shape of the color matrix to be row x col x channels \
    channels should 3 (R, G, and B channels of RGB colors)
    :type color_2d_array: numpy.ndarray
    :param mode: mode for displaying color matrix. "truncate" or "padding"
    :type mode: str
    :param figure_size: the size of the figure
    :type figure_size: tuple
    :param title: the title of the plot
    :type title: str
    :param axis_off: True to set the axis of the figure off
    :type axis_off: bool
    :param save_image: True to save the plot figure, False do not save the figure
    :type save_image: bool
    :param file_name: the path to the saved figure
    :type file_name: str
    :param return_matrix: True to return the processed color matrix back False not to return anything
    :type return_matrix: bool
    :param return_figure: Return the plotted figure, if true. Directly plot the color matrix if false
    :type return_figure: bool
    :return: the processed color matrix. Depending on the display mode, the return color matrix will have padding \
    white colors if mode is "padding", or the last row of color matrix will be truncated if mode is "truncate". \
    Or, return the figure with plotted color matrix if return_figure is True.
    :rtype: numpy.ndarray if return_matrix, matplotlib.pyplot.Figure if return_figure
    """
    assert len(color_2d_array.shape) == 3, "Only 2d array of three-channel color tuple/array accepted"
    assert color_2d_array.shape[-1] == 3, "The number of channels of color 2d array must be 3 (R, G, B)"
    assert mode == "truncate" or mode == "padding", "Invalid mode for displaying color matrix, two" \
                                                    "modes are available 'truncate' or 'padding'"
    # If the mode is padding
    if mode == "padding":
        # Flag variable False after appending the second column of colors to the color matrix
        first = True
        for color_col in color_2d_array:
            clr_chain = np.ones(shape=(1, 1, 3), dtype=np.uint8) * np.uint8(color_col[0])
            for i in range(len(color_2d_array[0]) - 1):
                try:
                    color = np.ones(shape=(1, 1, 3), dtype=np.uint8) * np.uint8(color_col[i + 1])
                except:
                    color = np.ones(shape=(1, 1, 3), dtype=np.uint8) * 255
                clr_chain = np.append(clr_chain, color, axis=0)
            if first:
                clr_matrix = np.ones(shape=clr_chain.shape, dtype=np.uint8) * 255
                first = False
            clr_matrix = np.append(clr_matrix, clr_chain, axis=1)
    # If the mode is truncate
    elif mode == "truncate":
        # If the last row has different length with the others
        if len(color_2d_array[-1]) != len(color_2d_array[-2]):
            # Truncate the last row
            clr_matrix = np.array(color_2d_array[:-1]).astype("uint8")
        else:
            # Otherwise keep the matrix
            clr_matrix = np.array(color_2d_array).astype("uint8")
        # Transpose the matrix to have a horizontal display
        clr_matrix = clr_matrix.transpose([1, 0, 2])

    if return_matrix:
        return clr_matrix

    fig = plt.figure(figsize=figure_size)
    plt.imshow(clr_matrix)
    plt.title(title)
    if axis_off:
        plt.axis('off')
    if save_image:
        plt.savefig(file_name)
    if return_figure:
        return fig

    plt.show()


def show_colors_in_cube(colors, figure_size=(8, 8), return_figure=False, sampling=-1, return_sampled_colors=False):
    """
    Show a sequence of RGB colors in cubic RGB space (e.g. R axis (x axis), G axis (y axis),
    and B axis (z axis))
    see https://matplotlib.org/3.1.1/gallery/mplot3d/scatter3d.html for more references
    ipympl is required for this function to work in the jupyter notebook

    :param colors: A sequence of colors to display in cubic space
    :type colors: numpy.ndarray
    :param figure_size: the size of the figure
    :type figure_size: tuple
    :param return_figure: Return the plotted figure and axes, if true \
                          Directly plot the cube, if false
    :type return_figure: bool
    :param sampling: Number of data points plot in the 3D cube. -1 to include all data in the plot
    :type sampling: int
    :param return_sampled_colors: Return the sampled out colors if True. Directly plot the colors in RGB cube if False
    :type return_sampled_colors: bool
    :return: return the figure and axes with plotted figure if return_figure is True \
    or, return the sampled out colors if return_sampled_colors is True
    :rtype: numpy.ndarray
    """
    assert colors.shape[-1] == 3, "The input colors must be a 2D numpy array with RGB colors where " \
                                  "shape of array is number of colors x channels(3)"

    if sampling > 0:
        sample_indices = np.random.choice(np.arange(colors.size // colors.shape[-1]), sampling, replace=False)
        colors = colors[sample_indices]

    # colors is the N*M x 3 version of the image.
    colors = np.concatenate([np.expand_dims(IC, axis=1) for IC in
                             [colors[..., 0].ravel(), colors[..., 1].ravel(), colors[..., 2].ravel()]], axis=1)

    if return_sampled_colors:
        return colors

    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111, projection='3d')

    if colors.max() > 1:
        ax.scatter(colors[..., 0], colors[..., 1], colors[..., 2], c=colors[..., :].astype("float32") / 255)
    else:
        ax.scatter(colors[..., 0], colors[..., 1], colors[..., 2], c=colors[..., :])

    # Label the axes.
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')

    if return_figure:
        return fig, ax

    plt.show()


def show_high_contrast_region(image, minimum_segment_size=0.0004, figsize=(6, 4), return_region_image=False):
    """
    Plot the high contrast region (brightness contrast) of the image.
    image is segmented using the gradient based watershed segmentation

    :param image: input color image shape=(row (height), col (width), channel(3))
    :type image: numpy.ndarray
    :param minimum_segment_size: The minimum size (in relative ratio [0, 1]) for the segments in the segmented image
    :type minimum_segment_size: float
    :param figsize: the size of the plot figure
    :type figsize: tuple
    :param return_region_image: Return the image with only high contrast region if True. \
                                Directly plot the image if False
    :type return_region_image: bool
    :return: If return_region_image is True, return the the image with only high contrast region. \
             region_image.shape == image.shape
    :rtype: numpy.ndarray
    """
    contrast_matrix, labeled_image = get_contrast_matrix_and_labeled_image(image,
                                                                           minimum_segment_size=minimum_segment_size)
    high_contrast_region_index = np.sum(contrast_matrix, axis=1).argmax()

    contrast_part = extract_region_with_index(image, high_contrast_region_index + 1, labeled_image)

    if return_region_image:
        return contrast_part

    plt.figure(figsize=figsize)
    plt.imshow(contrast_part)
    plt.show()


def show_low_contrast_region(image, minimum_segment_size=0.0004, figsize=(6, 4), return_region_image=False):
    """
    Plot the low contrast region (brightness contrast) of the image.
    image is segmented using the gradient based watershed segmentation

    :param image: input color image shape=(row (height), col (width), channel(3))
    :type image: numpy.ndarray
    :param minimum_segment_size: The minimum size (in relative ratio [0, 1]) for the segments in the segmented image
    :type minimum_segment_size: float
    :param figsize: the size of the plot figure
    :type figsize: tuple
    :param return_region_image: Return the image with only low contrast region if True. \
                                Directly plot the image if False
    :type return_region_image: bool
    :return: If return_region_image is True, return the the image with only low contrast region. \
             region_image.shape == image.shape
    :rtype: numpy.ndarray
    """
    contrast_matrix, labeled_image = get_contrast_matrix_and_labeled_image(image,
                                                                           minimum_segment_size=minimum_segment_size)
    low_contrast_region_index = np.sum(contrast_matrix, axis=1).argmin()

    contrast_part = extract_region_with_index(image, low_contrast_region_index + 1, labeled_image)

    if return_region_image:
        return contrast_part

    plt.figure(figsize=figsize)
    plt.imshow(contrast_part)
    plt.show()


def extract_region_with_index(image, region_index, labeled_image):
    """
    Helper function that masked the labeled image on the input image, and extract the
    region with corresponding region index in the labeled image from the input image

    :param image: input image shape=(row(height), col(width))
    :type image: numpy.ndarray
    :param region_index: the extracted region index in the labeled image
    :type region_index: int
    :param labeled_image: the labeled image of the corresponding input image shape=image.shape
    :type labeled_image: numpy.ndarray
    :return: Image with only region with corresponding index on labeled_image.
    :rtype: numpy.ndarray
    """
    extract_part = image.copy()
    # If the extracted region is bright, paint the background with black
    if np.average(image[labeled_image == region_index]) / float(image.max()) > 0.5:
        extract_part[labeled_image != region_index] = np.array([0, 0, 0], dtype=image.dtype)
    # If the extracted region is dark, paint the background with white
    else:
        # Get the max of image
        max = image.max()
        # If the image is 0-1 normalized
        if max <= 1:
            # White == [1, 1, 1]
            max = 1
        # If the image is 0-255 normalzied (uint8)
        else:
            # White == [255, 255, 255]
            max = 255
        extract_part[labeled_image != region_index] = np.array([max, max, max], dtype=image.dtype)

    return extract_part

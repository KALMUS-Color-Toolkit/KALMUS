import numpy as np
import matplotlib.pyplot as plt


def show_color(color, figure_size=(9, 6), title="Undefined Test",
                   axis_off=False, save_image=False, file_name="test.png"):
    """
    Plot the rgb color.
    :param color: 1D array contains the R, G, and B channel values
    :param title: The title of the plotted color
    :param axis_off: True to set the axis of the plot figure off. False to have the axis on the side of
    figure.
    :param save_image: True to save the plot figure into the path that user provide. False not to save
    the plot figure
    :param file_name: The filename of the saved figure. The default path to the saved image is test.png
    """
    # Generate a block image where each pixel of this block image is the plotted RGB color
    clr = np.ones(shape=(30, 30, 3), dtype=np.uint8) * np.uint8(color)
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


def show_colors_in_sequence(colors, figure_size=(9, 6), title="Undefined Test", axis_off=False, \
                        save_image=False, file_name="test.png", horizontal=True):
    """
    Plot a sequence of RGB colors either horizontally or vertically in line
    :param colors: 2D array of RGB colors. Expected sequence shape==Number of colors x channels (3)
    :param figure_size: the size of the plot figure
    :param title: the title of the plot
    :param axis_off: True to set the axis of the figure off. False to have the axis with the figure
    :param save_image: True to save the plot figure. False do not save figure
    :param file_name: the path of the saved figure
    :param horizontal: True to plot the sequence of colors horizontally, False to plot the sequence of colors vertically
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

    plt.figure(figsize=figure_size)
    plt.imshow(clr_chain)
    plt.title(title)
    if axis_off:
        plt.axis("off")
    if save_image:
        plt.savefig(file_name)
    plt.show()


def show_color_matrix(color_2d_array, mode="truncate", figure_size=(9, 4),
                      title="Undefined Test", axis_off=False,
                      save_image=False, file_name="Block.png", return_matrix=False, return_figure=False):
    """
    Show a matrix of colors (color barcodes). Two modes are available "truncate" and "padding"
    "truncate" mode will truncate the last row of the color matrix if it has different len with respect
    to the other rows. "padding" mode will pad white colors to the last row until the last row has the
    same length as the other rows
    :param color_2d_array: the input color matrix. Expected the shape of the color matrix to be row x col x channels
    channels should 3 (R, G, and B channels of RGB colors)
    :param mode: mode for displaying color matrix. "truncate" or "padding"
    :param figure_size: the size of the figure
    :param title: the title of the plot
    :param axis_off: True to set the axis of the figure off
    :param save_image: True to save the plot figure, False do not save the figure
    :param file_name: the path to the saved figure
    :param return_matrix: True to return the processed color matrix back False not to return anything
    :return: the process color matrix. Depending on the display mode, the return color matrix will have padding
    white colors if mode is "padding", or the last row of color matrix will be truncated if mode is "truncate"
    """
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

    if return_matrix:
        return clr_matrix


def show_image(img, title="Undefined Test", figure_size=(9, 6), axis_off=False):
    """
    Show the image in RGB color or in greyscale intensity
    :param img: input multi-channel color image or single-channel greyscale image
    :param title: The title of the plot image
    :param figure_size: The size of the plotted figure
    :param axis_off: True to set the axis of the figure to be off, False to have the axis with the figure
    """
    plt.figure(figsize=figure_size)
    plt.imshow(img)
    plt.title(title)
    if axis_off:
        plt.axis('off')
    plt.show()


def show_colors_in_cube(colors, figure_size=(8, 8), return_figure=False, sampling=-1):
    """
    Show a sequence of RGB colors in cubic RGB space (e.g. R axis (x axis), G axis (y axis),
    and B axis (z axis))
    see https://matplotlib.org/3.1.1/gallery/mplot3d/scatter3d.html for more references
    ipympl is required for this function to work in the jupyter notebook
    :param colors: A sequence of colors to display in cubic space
    :param figure_size: the size of the figure
    """
    assert colors.shape[-1] == 3, "The input colors must be a 2D numpy array with RGB colors where " \
                                  "shape of array is number of colors x channels(3)"
    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111, projection='3d')

    if sampling > 0:
        sample_indices = np.random.choice(np.arange(colors.size // colors.shape[-1]), sampling, replace=False)
        colors = colors[sample_indices]

    # Colors is the N*M x 3 version of the image.
    colors = np.concatenate([np.expand_dims(IC, axis = 1) for IC in
                        [colors[...,0].ravel(), colors[...,1].ravel(), colors[...,2].ravel()]], axis = 1)

    if colors.max() > 1:
        ax.scatter(colors[...,0], colors[...,1], colors[...,2], c=colors[..., :].astype("float32") / 255)
    else:
        ax.scatter(colors[..., 0], colors[..., 1], colors[..., 2], c=colors[..., :])

    # Label the axes.
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')

    if return_figure:
        return fig, ax

    plt.show()

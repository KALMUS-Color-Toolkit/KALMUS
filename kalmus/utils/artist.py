""" Utility artist """

import numpy as np
import cv2
import csv
from scipy import ndimage
from skimage.morphology import disk, remove_small_objects
from skimage.segmentation import watershed
from skimage.filters import rank, sobel
from skimage.future import graph
import scipy.stats as stats


def compute_dominant_color(image, n_clusters=3, max_iter=10, threshold_error=1.0, attempts=10):
    """
    Compute the dominant color of an input image using the kmeans clustering. The centers of the
    clusters are the dominant colors of the input image

    :param image: input image. Either a multi-channel color image or a grayscale image (2D image) \
    Expected shape of image is height x width x (channels)
    :type image: numpy.ndarray
    :param n_clusters: number of clusters
    :type n_clusters: int
    :param max_iter: maximum iterations before terminating kmeans clustering
    :type max_iter: int
    :param threshold_error: threshold error for terminating kmeans clustering. kmean clustering terminate \
    when the errors between the current computed and previous computed cluster center is under this \
    threshold
    :type threshold_error: float
    :param attempts: Number of attempts to rerun the Kmeans clustering with different initial cluster \
    centers. Since kmeans clustering randomly choose n number of cluster in its initialization process.
    :type attempts: int
    :return: An array of n cluster centers and an array of relative size (in percentage) of the clusters. \
    Expected output shape: n_clusters x channels (cluster centers), n_clusters (relative size in percentage) \
    E.g. for an input color image with 3 channels and n_clusters = 3  Output can be [[255, 255, 255], \
    [126, 75, 198], [186, 145, 122]], [0.4, 0.5, 0.1]
    :rtype: (numpy.ndarray, numpy.ndarray)
    """
    assert len(image.shape) >= 2, "The input must be a 2 dimensional image"
    # Flatten the image
    # If the image is in grayscale
    image = flatten_image(image)
    # make sure the dtype of the flatten image is np.float32
    image = np.float32(image)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iter, threshold_error)
    ret, label, centers = cv2.kmeans(image, n_clusters, None, criteria, attempts, cv2.KMEANS_RANDOM_CENTERS)

    percent_of_dominance = compute_percents_of_labels(label)

    return centers, percent_of_dominance


def flatten_image(image):
    """
    Flat the input 2D image into an 1D image while preserve the channels of the input image
    with shape==[height x width, channels]

    :param image: Input 2D image (either multi-channel color image or greyscale image)
    :type image: numpy.ndarray
    :return: The flatten 1D image. shape==(height x width, channels)
    :rtype: numpy.ndarry
    """
    assert len(image.shape) >= 2, "The input image must be a 2 Dimensional image"
    if len(image.shape) == 3:
        image = image.reshape((-1, image.shape[2]))
    elif len(image.shape) == 2:
        image = image.reshape((-1, 1))
    return image


def compute_percents_of_labels(label):
    """
    Compute the ratio/percentage size of the labels in an labeled image

    :param label: the labeled 2D image
    :type label: numpy.ndarray
    :return: An array of relative size of the labels in the image. Indices of the sizes in the array \
    is corresponding to the labels in the labeled image. E.g. output [0.2, 0.5, 0.3] means label 0's size \
    is 0.2 of the labeled image, label 1' size is 0.5 of the labeled image, and label 2's size is 0.3 of \
    the labeled image.
    :rtype: numpy.ndarray
    """
    # Get the bins of the histogram. Since the last bin of the histogram is [label, label+1]
    # We add 1 to the number of different labels in the labeled image when generating bins
    num_labels = np.arange(0, len(np.unique(label)) + 1)
    # Histogramize the label image and get the frequency array percent_of_dominance
    (percent_of_dominance, _) = np.histogram(label, bins=num_labels)
    # Convert the dtype of frequency array to float
    percent_of_dominance = percent_of_dominance.astype("float")
    # Normalized by the sum of frequencies (number of pixels in the labeled image)
    percent_of_dominance /= percent_of_dominance.sum()
    return percent_of_dominance


def compute_mode_color(image, bin_size=10):
    """
    compute the mode color of an input image

    :param image: either a multi-channel color image or a single channel greyscale image \
    Expected shape of image: height x width x (channels)
    :type image: numpy.ndarray
    :param bin_size: Histogramize the input image. Color/intensity of each pixel in the \
    image will be accumulate in the bins with size==bin_size. The output mode color/intensity \
    is always an integer multiple of the bin_size.
    :type bin_size: int
    :return: The mode color of the image (modes of the channels), shape=channels, and counts of the \
    mode colors happened in the input image, shape==channels
    :rtype: (numpy.ndarray, numpy.ndarray)
    """
    image = flatten_image(image)
    image = image // bin_size
    mode_color, counts = stats.mode(image, axis=0)
    return (mode_color[0] * bin_size), counts


def compute_mean_color(image):
    """
    Compute the average/mean color of the input multi-channel image or greyscale image.

    :param image: input image. Either a multi-channel color image or a single channel greyscale image
    :type image: numpy.ndarray
    :return: The average color of the image (averaged across the channels). shape==channels.
    :rtype: numpy.ndarray
    """
    image = flatten_image(image)
    avg_color = np.average(image, axis=0)
    return avg_color


def compute_median_color(image):
    """
    Compute the median color of the input multi-channel color image or a single channel greyscale image.

    :param image: input image. Either a multi-channel color image or a single channel greyscale image
    :type image: numpy.ndarray
    :return: The median color of the image (median values of channels), shape==channels
    :rtype: numpy.ndarray
    """
    image = flatten_image(image)
    median_color = np.median(image, axis=0)
    return median_color


def compute_brightest_color_and_brightness(grey_image, color_image, return_min=False,
                                           gaussian_blur=False, blur_radius=15):
    """
    Find the brightest pixel in an image and return the color and brightness at that pixel

    :param grey_image: The greyscale image. single channel 2D image. Expected shape==(row/height, col/width)
    :type grey_image: numpy.ndarray
    :param color_image: The corresponding color image. Expected shape==(row/height, col/width, channels)
    :type color_image: numpy.ndarray
    :param return_min: If true return the darkest color and brightness (of a pixel) as well
    :type return_min: bool
    :param gaussian_blur: Whether to apply a gaussian filter before finding the brightest point the grey image
    :type gaussian_blur: bool
    :param blur_radius: The radius of the gaussian filter
    :type blur_radius: int
    :return: The color and brightness of the brightest pixel (, color and brightness of the darkest pixel)
    :rtype: (numpy.ndarray, int, tuple)
    """
    if gaussian_blur:
        grey_image = cv2.GaussianBlur(grey_image.copy(), (blur_radius, blur_radius), 0)
    min_brightness, max_brightness, min_loc, max_loc = cv2.minMaxLoc(grey_image)
    if return_min:
        return color_image[max_loc[::-1]], max_brightness, max_loc[::-1], \
               color_image[min_loc[::-1]], min_brightness, min_loc[::-1]
    else:
        return color_image[max_loc[::-1]], max_brightness, max_loc[::-1]


def find_bright_spots(image, n_clusters=3, blur_radius=21, amount_of_bright_parts=0.8, return_all_pos=False):
    """
    Find the indices location of the top-k brightest spots in an color image.

    :param image: input image. Must be an mutli-channel RGB color image
    :type image: numpy.ndarray
    :param n_clusters: expected number of clusters/brightest spots in the input image
    :type n_clusters: int
    :param blur_radius: radius of the Gaussian blur kernel that used to smooth the image
    :type blur_radius: int
    :param amount_of_bright_parts: amount of bright parts in an image. Used to find the lower bound for \
    distinguishing the bright and non-bright part of the input image. Range of amount_of_bright_parts is \
    in [0, 1] (all non-bright -> all bright)
    :type amount_of_bright_parts: float
    :return: The location of centers of top-3 bright spots (with irregular shape), percentage of dominance of each spot \
    (relative size of the spot)
    :rtype: (numpy.ndarray, numpy.ndarray)
    """
    assert amount_of_bright_parts >= 0 and amount_of_bright_parts <= 1, "Range of the sample ration is in [0, 1]"
    assert n_clusters >= 1, "The number of bright spots must be larger or equal to 1"

    amount_of_bright_parts = amount_of_bright_parts * 100
    # Convert BRG to Greyscale
    grayscale_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Blur the image with radius = blurRadius
    blurred_img = cv2.GaussianBlur(grayscale_img, (blur_radius, blur_radius), 0)

    # Compute the lower bound threshold
    lower_bound = np.percentile(blurred_img, 100 - amount_of_bright_parts) - 1

    # Threshold the imgae by setting any pixel with value larger than lower bound to 255
    threshed_img = cv2.threshold(blurred_img, lower_bound, 255, cv2.THRESH_BINARY)[1]

    # Purifiy the edges of the brightest spots.
    threshed_img = cv2.erode(threshed_img, None, iterations=2)
    threshed_img = cv2.dilate(threshed_img, None, iterations=4)

    # Get the location of all white pixel in binary threshold image
    locs = np.argwhere(threshed_img == 255)
    try:
        # convert to np.float32
        locs_above_threshold = np.float32(locs)

        # define criteria and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(locs_above_threshold, n_clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Compute the percentage of each clusters in the image.
        percent_of_dominance = compute_percents_of_labels(label)

        if return_all_pos:
            return label, locs_above_threshold.astype("int32"), percent_of_dominance
        else:
            return center.astype("int32"), percent_of_dominance

    except:
        # Catch exception return negative array.
        if return_all_pos:
            return np.array([-1]), np.array([-1]), np.array([-1])
        else:
            return np.ones(shape=(n_clusters, 1)) * -1, np.ones(shape=(n_clusters, 1)) * -1


def random_sample_pixels(image, sample_ratio=0, mode="row-col"):
    """
    Randomly sample an amount of pixels from an image based on the given sampled ratio.
    Two sampling mode are available.
    row-col: sampling first across the row and then across the column on each sampled row
    The output sampled image is still 2D and keep same aspect ratio as the input image, which
    can be used to visualize the sampling effect on the image.
    flat: sampling across the flat input image. The shape and aspect ratio of the input image
    are not preserved due to the flatten process, but it sample the pixels much faster than
    'row-col' mode. The distribution of the sampling result is similar to that from the 'row-col'

    :param image: Input 2D image. Either a multi-channel color image or a single channel greyscale image \
    Expected shape==height x width x (channels)
    :type image: numpy.ndarray
    :param sample_ratio: The amount of pixels sampled from the image. in range [0, 1]
    :type sample_ratio: float
    :param mode: two sampling mode are available. \
    1) 'row-col' sampling mode \
    2) 'flat' sampling mode
    :type mode: str
    :return: If mode="flat", return the resampled array of pixels (1-d flat array of data points) \
             If mode="row-col", return the resampled image
    :rtype: numpy.ndarray
    """
    assert 0 <= sample_ratio <= 1, "The sample ratio is in the range of [0, 1]"
    if sample_ratio == 1:
        return image
    elif sample_ratio == 0:
        return np.array([]).astype(image.dtype)
    if mode == "row-col":
        # To keep the aspect ratio of the input image, sample equal ratio on the columns and rows
        ratio = (sample_ratio) ** (1 / 2)
        # Number of row to sample
        row_size = int(image.shape[0] * ratio)
        # Number of column to sample
        col_size = int(image.shape[1] * ratio)
        # Sample the row first
        random_row_indices = np.sort(np.random.choice(np.arange(image.shape[0]), row_size, replace=False))
        random_row = image[random_row_indices]
        random_pixels = []
        # Then, in each row, sampled a number of pixels/columns
        for row in random_row:
            random_col_indices = np.sort(np.random.choice(np.arange(image.shape[1]), col_size, replace=False))
            random_pixels.append(row[random_col_indices])
        random_pixels = np.array(random_pixels)
    elif mode == "flat":
        # Flatten the image
        flat_img = flatten_image(image)
        # Generate the possible indices
        indices = np.arange(flat_img.shape[0])
        # Generate the sampled indices
        sampled_indices = np.random.choice(indices, int(sample_ratio * flat_img.shape[0]), replace=False)
        # Sampled the flat image using the sampled indices
        random_pixels = flat_img[sampled_indices]
    else:
        # If none of two modes is specified
        print("Invalid sampling mode. Two sampling options are 'row-col' and 'flat'")
        return
    return np.array(random_pixels)


def watershed_segmentation(image, minimum_segment_size=0.0004, base_ratio=0.5, denoise_disk_size=5,
                           gradiant_disk_size=5,
                           marker_disk_size=15):
    """
    Label the connected regions in an image.
    Use edge detection approach with watershed algorithm.
    adjust the critical gradient (edge gradient) with the distribution of the input image's
    intensity gradient .

    :param image: The input color image for region segmentation using gradient-based watershed
    :type image: numpy.ndarray
    :param minimum_segment_size: The minimum size of the segments in the segmented image in percentage \
    (size is the relative ratio of the image) The segmented regions smaller than the minimum size will be merged \
    to its neighboring larger segmented components
    :type minimum_segment_size: float
    :param base_ratio: Amount of regions at least in the image. The image in watershed transformation is \
    differentiated into two parts regions + boundaries. The base ratio is the ratio between the least amount of \
    pixels that are regions and the total amount of pixels in the image.
    :type base_ratio: float
    :param denoise_disk_size: the kernel size of the denoise median filter
    :type denoise_disk_size: int
    :param gradiant_disk_size: the kernel size of the gradient filter that is used for determining the amount of \
    boundaries
    :type gradiant_disk_size: int
    :param marker_disk_size: the kernel size of the gradient filter that is used for generating transformation \
    marker
    :type marker_disk_size: int
    :return: the segmented image, where shape==input_image.shape. and regions are labeled from 0 to n-1, where \
    n is the number of regions in the labeled image. Functions also return the greyscale image corresponding to \
    the original image
    :rtype: (numpy.ndarray, numpy.ndarray)
    """
    assert 0 <= minimum_segment_size < 1, "The minimum size of the segments (in percentage ratio) is in range [0, 1)"
    # Gray Scale image
    grey_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # denoise image
    denoised = rank.median(grey_image, disk(denoise_disk_size))

    num_of_pixels = image.shape[0] * image.shape[1]

    # local gradient
    gradient = rank.gradient(denoised, disk(gradiant_disk_size))
    critical = np.sort(gradient, axis=None)

    # Use std to adjust the ratio of the regions in the image
    criteria = np.std(gradient)
    # A high std of the image's intensity gradient means the intensities of image are changed more rapidly
    # and frequently, so there are more boundaries but less regions. A low std of the image's intensity
    # gradients means the changes across the image are more smooth. Such coherence indicate a larger ratio
    # of regions in the image
    # Divide adjust ratio by the std of the gradient distribution
    adjust_ratio = 0.25 * 25 / (criteria + 1e6)
    if (adjust_ratio > 0.45):
        adjust_ratio = 0.45
    # Assume at least 50% of an image is the content (at most 50% of an image
    # is edge), and at most 95% of an image is the content (at least 5% of an
    # image is edge)
    # Critical is the critical threshold of intensity gradient that separate the regions and boundaries
    # Pixels with gradients larger than critical are considered as boundaries
    # Pixels with gradients smaller than critical are considered as regions
    critical = critical[int(num_of_pixels * (base_ratio + adjust_ratio))]

    # Minimum size of a segment
    # Segments under the minimum size will be joined into larger segments
    segment_min_size = int(num_of_pixels * minimum_segment_size)
    # find continuous region which marked by gradient lower than critical gradient
    markers = rank.gradient(denoised, disk(marker_disk_size)) < critical
    markers = ndimage.label(remove_small_objects(markers, segment_min_size))[0]

    # process the watershed transformation
    regions = watershed(gradient, markers)

    # Return the labeled image and the corresponding greyscale image
    return regions, grey_image


def get_rag(gray_image, labels):
    """
    Get the region adjacency graph using the labeled image and corresponding the edge map generated by
    greyscale image with sobel filter

    :param gray_image: The greyscale image corresponding to the labeled image
    :type gray_image: numpy.ndarray
    :param labels: a labeled segmented image, where the pixels in the image are labeled with index of the \
    segmented regions.
    :type labels: numpy.ndarray
    :return: The region adjacency graph in dictionary \
    see https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_rag_boundary.html for more \
    references
    :rtype: skimage.future.graph.RAG
    """
    # Get rag of the labeled image
    edge_map = sobel(gray_image)
    rag = graph.rag_boundary(labels, edge_map)
    return rag


def rag_to_matrix(rag, num_regions):
    """
    Transfer the region adjacency dictionary to a more accessible region adjacency matrix
    where in the matrix, 1 means the region of corresponding column index is adjacent to the
    region of corresponding row index/
    e.g.
    0,1
    1,0 means region 0 and region 1 are adjacent

    :param rag: region adjacency dictionary
    :type rag: skimage.future.graph.RAG
    :param num_regions: number of regions in the region adjacency graph
    :type num_regions: int
    :return: An binary adjacency matrix with shape==num_regions x num_regions
    :rtype: numpy.ndarray
    """
    matrix = np.zeros((num_regions, num_regions), dtype=np.int8)
    for i in range(1, num_regions + 1):
        elements = rag[i]
        adict = dict(elements)
        adj_list = adict.keys()
        for keys in adj_list:
            matrix[i - 1][keys - 1] = 1
    return matrix


def color_of_regions(labels, original_image):
    """
    Compute average color and brightest color of the regions and record
    the relative size of the regions as a ratio with respect to the size
    of whole image.

    :param labels: The labeled image. Expected shape==height x width. Integer labels
    :type labels: numpy.ndarray
    :param original_image: The original color image corresponding to the label image
    :type original_image: numpy.ndarray
    :return: A list of average color of the regions, a list of brightest color of the regions, and \
    a list of sizes of the regions. The order of the regions in list is the same as they are in \
    labeled image
    :rtype: (list, list, list)
    """
    # Average Color of the region
    avg_colors_list = []

    # Brightest Color of the region
    brightest_colors_list = []

    # Sizes of the regions in the image.
    region_sizes = []

    # Size of the whole image in pixels
    num_of_pixels = original_image.shape[0] * original_image.shape[1]

    # Set of labels in the image
    labels_set = np.unique(labels)
    # Greyscale image
    grey_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)

    for region in labels_set:
        indices = labels == region

        # Extract the color info of regions from the original image
        extract_image = original_image[indices]
        region_sizes.append(len(extract_image) / num_of_pixels)
        average_color = np.average(extract_image, axis=0)
        avg_colors_list.append(average_color)

        # Extract the brightness related info of regions from the greyscale image
        extract_gray_image = grey_image[indices]
        brightest_color_loc = np.argmax(extract_gray_image)
        brightest_color = extract_image[brightest_color_loc]
        brightest_colors_list.append(brightest_color)

    return avg_colors_list, brightest_colors_list, region_sizes


def contrast_between_regions(region_colors, matrix, region_weights=None):
    """
    Compute the contrast between the segmented regions in image using the color of regions
    and adjacency matrix

    :param region_colors: A list of colors of segmented regions
    :type region_colors: list
    :param matrix: A 2D adjacency matrix that describe the spatial relationship between the regions \
    Expect a binary matrix, where 1 means adjacent and 0 means non-adjacent
    :type matrix: numpy.ndarray
    :param region_weights: A 1D array of weights that can be applied onto the contrast calculate for each \
    regions. \
    e.g. Regions may have different sizes, and you can weight the computed contrast by the size of the \
    regions. Expected shape of the regions weight is shape==number of regions
    :type region_weights: list
    :return: A 2D numpy matrix where each entry is the contrast between the row indexed region and column \
    indexed region. Contrast ratio >= 1, an entry with 0 means row indexed region and column indexed region \
    are non-adjacent
    :rtype: list
    """
    assert matrix.shape[0] == matrix.shape[1], "Invalid shape of the adjacency matrix, the matrix must" \
                                               "be a 2D binary numpy array with a square shape. shape[0]" \
                                               "==shape[1]"
    assert matrix.shape[0] == len(region_colors), "Incompatible adjacency matrix with region_colors," \
                                                  " different number of regions in matrix and region_colors" \
                                                  " list"
    # List of row that contains the contrast between two regions
    contrast_list = []
    # If no region weights are given, then use the uniform weights
    if region_weights is None:
        region_weights = np.ones(shape=len(matrix))

    # Compute the contrast between each adjacent regions
    for i in range(len(matrix)):
        contrast_row = []
        for j in range(len(matrix[0])):
            # If two regions are adjacent
            if matrix[i][j] != 0:
                # Compute the contrast and append it to the list
                contrast = contrast_ratio(region_colors[i], region_colors[j]) * region_weights[i]
                contrast_row.append(contrast)
            else:
                # Else append 0 as non-adjacent
                contrast_row.append(0)
        contrast_list.append(contrast_row)
    contrast_list = np.array(contrast_list)

    return contrast_list


def _RGB2sRGB(RGB):
    """
    Convert the 24-bits Adobe RGB color to the standard RGB color defined
    in Web Content Accessibility Guidelines (WCAG) 2.0
    see https://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef for more references

    :param RGB: The input RGB color or colors shape== ... x 3 (R, G, and B channels)
    :type RGB: numpy.ndarray
    :return: converted sRGB colors
    :rtype: numpy.ndarray
    """
    sRGB = RGB / 255
    return sRGB


def _sRGB2luminance(sRGB):
    """
    Compute luminance of standard RGB color
    see https://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef for more references

    :param sRGB: Input sRGB color or colors shape==... x 3 (sR, sG, and sB channels)
    :type sRGB: numpy.ndarray
    :return: the luminance computed using the sRGB color
    :rtype: float
    """
    lRGB = np.zeros(shape=sRGB.shape)
    lRGB[sRGB <= 0.03928] = sRGB[sRGB <= 0.03928] / 12.92
    lRGB[sRGB > 0.03928] = ((sRGB[sRGB > 0.03928] + 0.055) / 1.055) ** 2.4
    luminance = 0.2126 * lRGB[..., 0] + 0.7152 * lRGB[..., 1] + 0.0722 * lRGB[..., 2]
    return luminance


def contrast_ratio(color1, color2):
    """
    Compute the contrast ratio between two 24-bits RGB colors in range [0, 255]
    see https://www.w3.org/TR/2008/REC-WCAG20-20081211/#contrast-ratiodef for more references

    :param color1: one of the 24-bits RGB colors in range [0, 255]
    :type color1: numpy.ndarray
    :param color2: one of the 24-bits RGB colors in range [0, 255]
    :type color2: numpy.ndarray
    :return: the contrast ratio between two 24-bits RGB colors. Contrast ratio >= 1
    :rtype: float
    """
    luminance1 = _sRGB2luminance(_RGB2sRGB(color1))
    luminance2 = _sRGB2luminance(_RGB2sRGB(color2))
    ratio = (luminance1 + 0.05) / (luminance2 + 0.05)
    if ratio < 1:
        ratio = 1 / ratio
    return ratio


def get_contrast_matrix_and_labeled_image(frame, minimum_segment_size=0.0004):
    """
    Helper function that use the watershed method to segment the input image return the matrix of the
    brightness contrast of each segmented region with respect to its neighbors (adjacent segmented regions)

    :param frame: The input frame
    :type frame: numpy.ndarray
    :param minimum_segment_size: The minimum size of the segmented region in the ratio to the whole frame. Range (0, 1)
    :type minimum_segment_size: float
    :return: The matrix with shape (num_regions x num_regions) whose cell [i, j] represents the contrast \
             between the region i and region j, and the corresponding labeled image (segmentation)
    :rtype: (list, numpy.ndarray)

    """
    labels, grey_frame = watershed_segmentation(frame, minimum_segment_size=minimum_segment_size)
    try:
        adjacency_matrix = rag_to_matrix(get_rag(grey_frame, labels), len(np.unique(labels)))
        avg_color, _, region_sizes = color_of_regions(labels, frame)
        contrast_matrix = contrast_between_regions(avg_color, adjacency_matrix)
    except:
        contrast_matrix = np.array([[0]])
        labels = np.ones(shape=frame.shape)
    return contrast_matrix, labels


def grabcut_foreback_segmentation(image, start_row=0, start_col=0, row_size=-1, col_size=-1, num_iter=3,
                                  return_masks=False):
    """
    Perform the GrabCut segmentation over the input image with a rectangle of possible foreground
    specified by user. The GrabCut segment the image into two parts foreground and background, and
    the function return the 1D image of the foreground and background as the output

    :param image: The input image for GrabCut segmentation
    :type image: numpy.ndarray
    :param start_row: The starting row of the foreground rectangle of possible foreground
    :type start_row: int
    :param start_col: The starting col of the foreground rectangle of possible foreground
    :type start_col: int
    :param row_size: The vertical length of the rectangle
    :type row_size: int
    :param col_size: The horizontal length of the rectangle
    :type col_size: int
    :param num_iter: The number of iterations for GrabCut to run
    :type num_iter: int
    :param return_masks: Return the foreground and background boolean mask if True \
                         Return the 1D image of foreground pixels and 1D image of background pixels if False \
                         False by default
    :type return_masks: bool
    :return: If return_masks is False (default), 1D image of the foreground part of the image, and 1D image of \
             the background part of the image Expected shape== Number of pixels x channels. \
             If return_masks is True, return boolean masks foreground and background. Expected shape==image.shape

    :rtype: (numpy.ndarray, numpy.ndarray)
    """
    if start_row < 0:
        start_row = 0
    if start_col <= 0:
        start_col = image.shape[1] // 6
    if row_size <= 0:
        row_size = image.shape[0] - 1
    if col_size <= 0:
        col_size = image.shape[1] * 2 // 3

    mask = np.zeros(image.shape[:2], np.uint8)
    # Temporary array for background Gaussian mixture model
    background_model = np.zeros((1, 65), np.float64)
    # Temporary array for foreground Gaussian mixture model
    foreground_model = np.zeros((1, 65), np.float64)
    # Rectangle box for possible foreground
    rectangle = (start_col, start_row, col_size, row_size)
    cv2.grabCut(image, mask, rectangle,
                background_model, foreground_model,
                num_iter, cv2.GC_INIT_WITH_RECT)
    if return_masks:
        # The obvious foreground and probable foreground are marked with 1 and 3
        # The obvious background and probable background are marked with 0 and 2
        return (mask == 1) | (mask == 3), (mask == 0) | (mask == 2)
    else:
        # The obvious foreground and probable foreground are marked with 1 and 3
        foreground_image = image[(mask == 1) | (mask == 3)]
        # The obvious background and probable background are marked with 0 and 2
        background_image = image[(mask == 0) | (mask == 2)]

    return foreground_image, background_image


def find_letter_box_from_videos(video, num_sample=30):
    """
    Find the position of letterbox (black bars around the scene) in the input cv2 video object.
    The function samples out num_sample (20 by default) number of frames from cv2 video object, and find the position
    of letterbox in each frame. The function uses the median results from all sampled frames as the final position of
    video's letterbox.

    Notice that the function assumes the letterbox is black or very close to black.

    :param video: Input video object captured by cv2.VideoCapture()
    :type video: cv2.VideoCapture
    :param num_sample: Number of frames to sample from video for finding letterbox
    :type num_sample: int
    :return: The smaller row index of letterbox (bound for upper horizontal letterbox), \
             the larger row index of letterbox (bound for lower horizontal letterbox), \
             the smaller col index of letterbox (bound for left vertical letterbox), \
             and the larger col index of letterbox (bound for right vertical letterbox). \
             \
             The results are the median results on num_sample number of frames
    :rtype: (int, int, int, int)

    """
    film_length_in_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Sampled out num_sample number of frames from input video
    possible_indexes = np.arange(film_length_in_frames // 6, film_length_in_frames * 5 // 6, 1)
    frame_indexes = np.random.choice(possible_indexes, num_sample, replace=True)

    # list of possible smaller row indexes (bounding the upper letterbox)
    possible_low_bound_ver = []
    # list of possible larger row indexes (bounding the lower letterbox)
    possible_high_bound_ver = []
    # list of possible smaller column indexes (bounding the left letterbox)
    possible_low_bound_hor = []
    # list of possible larger column indexes (bounding the right letterbox)
    possible_high_bound_hor = []

    # Find the letterbox position on each sampled frame
    for frame_index in frame_indexes:
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = video.read()
        if success:
            low_bound_v, high_bound_v, low_bound_h, high_bound_h = get_letter_box_from_frames(frame)
            possible_low_bound_ver.append(low_bound_v)
            possible_high_bound_ver.append(high_bound_v)
            possible_low_bound_hor.append(low_bound_h)
            possible_high_bound_hor.append(high_bound_h)

    # Take the medians as final results
    low_bound_ver = int(np.median(possible_low_bound_ver))
    high_bound_ver = int(np.median(possible_high_bound_ver))
    low_bound_hor = int(np.median(possible_low_bound_hor))
    high_bound_hor = int(np.median(possible_high_bound_hor))

    return low_bound_ver, high_bound_ver, low_bound_hor, high_bound_hor


def get_letter_box_from_frames(frame, threshold=5):
    """
    Find the position of letterbox (black bars around the scene) in the input cv2 video object.
    The function assumes the letter box of the frame is black (dark)

    :param frame: Input frame
    :type frame: numpy.ndarray
    :param threshold: The brightness threshold value that distinguish \
                      the region of interest (bright) and letterbox (dark)
    :type threshold: int
    :return: The smaller row index of letterbox (bound for upper horizontal letterbox), \
             the larger row index of letterbox (bound for lower horizontal letterbox), \
             the smaller col index of letterbox (bound for left vertical letterbox), \
             and the larger col index of letterbox (bound for right vertical letterbox).
    :rtype: (int, int, int, int)
    """
    low_bound_ver = 0
    high_bound_ver = frame.shape[0]
    low_bound_hor = 0
    high_bound_hor = frame.shape[1]

    for i in range(0, frame.shape[0] // 2):
        color = np.average(frame[i, ...])
        if color > threshold:
            low_bound_ver = i
            break

    for i in range(frame.shape[0] - 1, frame.shape[0] // 2 - 1, -1):
        color = np.average(frame[i, ...])
        if color > threshold:
            high_bound_ver = i
            break

    for j in range(0, frame.shape[1] // 2):
        color = np.average(frame[:, j, ...])
        if color > threshold:
            low_bound_hor = j
            break

    for j in range(frame.shape[1] - 1, frame.shape[1] // 2 - 1, -1):
        color = np.average(frame[:, j, ...])
        if color > threshold:
            high_bound_hor = j
            break

    return low_bound_ver, high_bound_ver + 1, low_bound_hor, high_bound_hor + 1


def write_in_info(info_row, file_name="output.csv", mode='a'):
    """
    Write a row of information to the csv file with a python list (not numpy array).
    All the values in numpy array (such as colors) are recommended to be converted to the list
    before write into the info_row.

    :param info_row: A row of data that will be write to the target csv file
    :type info_row: list
    :param file_name: The name of the csv file
    :type file_name: str
    :param mode: The mode for using the file
    :type mode: str
    """
    with open(file_name, newline="", mode=mode) as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(info_row)

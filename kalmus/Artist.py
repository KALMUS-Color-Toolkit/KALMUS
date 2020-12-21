""" Utility Artist """

import numpy as np
import cv2
import csv
from scipy import ndimage
from skimage.morphology import watershed, disk, remove_small_objects
from skimage.filters import rank, sobel
from skimage.future import graph
import scipy.stats as stats


def compute_dominant_color(image, n_clusters=3, max_iter=10, threshold_error=1.0, attempts=10):
    """
    Compute the dominant color of an input image using the kmeans clustering. The centers of the
    clusters are the dominant colors of the input image
    :param image: input image. Either a multi-channel color image or a grayscale image (2D image)
    Expected shape of image is height x width x (channels)
    :param n_clusters: number of clusters
    :param max_iter: maximum iterations before terminating kmeans clustering
    :param threshold_error: threshold error for terminating kmeans clustering. kmean clustering terminate
    when the errors between the current computed and previous computed cluster center is under this
    threshold
    :param attempts: Number of attempts to rerun the Kmeans clustering with different initial cluster
    centers. Since kmeans clustering randomly choose n number of cluster in its initialization process.
    :return: An array of n cluster centers and an array of relative size (in percentage) of the clusters.
    Expected output shape: n_clusters x channels (cluster centers), n_clusters (relative size in percentage)
    E.g. for an input color image with 3 channels and n_clusters = 3  Output can be [[255, 255, 255],
    [126, 75, 198], [186, 145, 122]], [0.4, 0.5, 0.1]
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
    :return: The flatten 1D image. shape==(height x width, channels)
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
    :return: An array of relative size of the labels in the image. Indices of the sizes in the array
    is corresponding to the labels in the labeled image. E.g. output [0.2, 0.5, 0.3] means label 0's size
    is 0.2 of the labeled image, label 1' size is 0.5 of the labeled image, and label 2's size is 0.3 of
    the labeled image.
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


def compute_mode_color(image, bin_size = 10):
    """
    compute the mode color of an input image
    :param image: either a multi-channel color image or a single channel greyscale image
    Expected shape of image: height x width x (channels)
    :param bin_size: Histogramize the input image. Color/intensity of each pixel in the
    image will be accumulate in the bins with size==bin_size. The output mode color/intensity
    is always an integer multiple of the bin_size.
    :return: The mode color of the image (modes of the channels), shape=channels, and counts of the
    mode colors happened in the input image, shape==channels
    """
    image = flatten_image(image)
    image = image // bin_size
    mode_color, counts = stats.mode(image, axis=0)
    return (mode_color[0] * bin_size), counts


def compute_mean_color(image):
    """
    Compute the average/mean color of the input multi-channel image or greyscale image.
    :param image: input image. Either a multi-channel color image or a single channel greyscale image
    :return: The average color of the image (averaged across the channels). shape==channels.
    """
    image = flatten_image(image)
    avg_color = np.average(image, axis=0)
    return avg_color


def compute_median_color(image):
    """
    Compute the median color of the input multi-channel color image or a single channel greyscale image.
    :param image: input image. Either a multi-channel color image or a single channel greyscale image
    :return: The median color of the image (median values of channels), shape==channels
    """
    image = flatten_image(image)
    median_color = np.median(image, axis=0)
    return median_color


def compute_brightest_color_and_brightness(grey_image, color_image, return_min=False,
                                           gaussian_blur=False, blur_radius=15):
    """
    Find the brightest pixel in an image and return the color and brightness at that pixel
    :param blur_radius: The radius of the gaussian filter
    :param gaussian_blur: Whether to apply a gaussian filter before finding the brightest point the grey image
    :param grey_image: The greyscale image. single channel 2D image. Expected shape==(row/height, col/width)
    :param color_image: The corresponding color image. Expected shape==(row/height, col/width, channels)
    :param return_min: If true return the color and brightness of the darkest pixel as well
    :return: The color and brightness of the brightest pixel (, color and brightness of the darkest pixel)
    """
    if gaussian_blur:
        grey_image = cv2.GaussianBlur(grey_image.copy(), (blur_radius, blur_radius), 0)
    min_brightness, max_brightness, min_loc, max_loc = cv2.minMaxLoc(grey_image)
    if return_min:
        return color_image[max_loc[::-1]], max_brightness, max_loc[::-1],\
                color_image[min_loc[::-1]], min_brightness, min_loc[::-1]
    else:
        return color_image[max_loc[::-1]], max_brightness, max_loc[::-1]


def find_bright_spots(image, n_clusters=3, blur_radius=21, amount_of_bright_parts=0.8, return_all_pos=False):
    """
    Find the indices location of the top-k brightest spots in an color image.
    :param image: input image. Must be an mutli-channel RGB color image
    :param n_clusters: expected number of clusters/brightest spots in the input image
    :param blur_radius: radius of the Gaussian blur kernel that used to smooth the image
    :param amount_of_bright_parts: amount of bright parts in an image. Used to find the lower bound for
    distinguishing the bright and non-bright part of the input image. Range of amount_of_bright_parts is
    in [0, 1] (all non-bright -> all bright)
    :return:
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
    locs = np.argwhere(threshed_img==255)
    try:
        # convert to np.float32
        Z = np.float32(locs)

        # define criteria and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(Z, n_clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Compute the percentage of each clusters in the image.
        percent_of_dominance = compute_percents_of_labels(label)

        if return_all_pos:
            return label, Z.astype("int32"), percent_of_dominance
        else:
            return center.astype("int32"), percent_of_dominance

    except:
        # Catch exception return negative array.
        if return_all_pos:
            return np.array([-1]), np.array([-1]), np.array([-1])
        else:
            return np.array([[-1], [-1], [-1]]), np.array([[-1], [-1], [-1]])


def random_sample_pixels(img, sample_ratio=0, mode="row-col"):
    """
    Randomly sample an amount of pixels from an image based on the given sampled ratio.
    Two sampling mode are available.
    row-col: sampling first across the row and then across the column on each sampled row
    The output sampled image is still 2D and keep same aspect ratio as the input image, which
    can be used to visualize the sampling effect on the image.
    flat: sampling across the flat input image. The shape and aspect ratio of the input image
    are not preserved due to the flatten process, but it sample the pixels much faster than
    'row-col' mode. The distribution of the sampling result is similar to that from the 'row-col'
    :param img: Input 2D image. Either a multi-channel color image or a single channel greyscale image
    Expected shape==height x width x (channels)
    :param sample_ratio: The amount of pixels sampled from the image. in range [0, 1]
    :param mode: two sampling mode are available.
    1) 'row-col' sampling mode 2) 'flat' sampling mode
    :return:
    """
    assert 0 <= sample_ratio <= 1, "The sample ratio is in the range of [0, 1]"
    if sample_ratio == 1:
        return img
    elif sample_ratio == 0:
        return np.array([]).astype(img.dtype)
    if mode == "row-col":
        # To keep the aspect ratio of the input image, sample equal ratio on the columns and rows
        ratio = (sample_ratio) ** (1 / 2)
        # Number of row to sample
        row_size = int(img.shape[0] * ratio)
        # Number of column to sample
        col_size = int(img.shape[1] * ratio)
        # Sample the row first
        random_row_indices = np.sort(np.random.choice(np.arange(img.shape[0]), row_size, replace=False))
        random_row = img[random_row_indices]
        random_pixels = []
        # Then, in each row, sampled a number of pixels/columns
        for row in random_row:
            random_col_indices = np.sort(np.random.choice(np.arange(img.shape[1]), col_size, replace=False))
            random_pixels.append(row[random_col_indices])
        random_pixels = np.array(random_pixels)
    elif mode == "flat":
        # Flatten the image
        flat_img = flatten_image(img)
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


def watershed_segmentation(image, minimum_segment_size=0.0004, base_ratio=0.5, denoise_disk_size = 5, gradiant_disk_size = 5,
                           marker_disk_size=15):
    """
    Label the connected regions in an image.
    Use edge detection approach with watershed algorithm.
    adjust the critical gradient (edge gradient) with the distribution of the input image's
    intensity gradient .
    :param grey_image: The input image for region segmentation
    :param minimum_segment_size: The minimum size of the segments in the segmented image in percentage
    (size is the relative ratio of the image) The segmented regions smaller than the minimum size will be merged
    to its neighboring larger segmented components
    :param base_ratio: Amount of regions at least in the image. The image in watershed transformation is
    differentiated into two parts regions + boundaries. The base ratio is the ratio between the least amount of 
    pixels that are regions and the total amount of pixels in the image.
    :param denoise_disk_size: the kernel size of the denoise median filter
    :param gradiant_disk_size: the kernel size of the gradient filter that is used for determining the amount of 
    boundaries
    :param marker_disk_size: the kernel size of the gradient filter that is used for generating transformation 
    marker
    :return: the segmented image, where shape==input_image.shape. and regions are labeled from 0 to n-1, where
    n is the number of regions in the labeled image. Functions also return the greyscale image corresponding to
    the original image
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
    :param labels: a labeled segmented image, where the pixels in the image are labeled with index of the
    segmented regions.
    :return: The region adjacency graph in dictionary
    see https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_rag_boundary.html for more
    references
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
    :param num_regions: number of regions in the region adjacency graph
    :return: An binary adjacency matrix with shape==num_regions x num_regions
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
    :param original_image: The original color image corresponding to the label image
    :return: A list of average color of the regions, a list of brightest color of the regions, and
    a list of sizes of the regions. The order of the regions in list is the same as they are in
    labeled image
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
    :param matrix: A 2D adjacency matrix that describe the spatial relationship between the regions
    Expect a binary matrix, where 1 means adjacent and 0 means non-adjacent
    :param region_weights: A 1D array of weights that can be applied onto the contrast calculate for each
    regions.
    e.g. Regions may have different sizes, and you can weight the computed contrast by the size of the
    regions. Expected shape of the regions weight is shape==number of regions
    :return: A 2D numpy matrix where each entry is the contrast between the row indexed region and column
    indexed region. Contrast ratio >= 1, an entry with 0 means row indexed region and column indexed region
    are non-adjacent
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
    :return: converted sRGB colors
    """
    sRGB = RGB / 255
    return sRGB


def _sRGB2luminance(sRGB):
    """
    Compute luminance of standard RGB color
    see https://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef for more references
    :param sRGB: Input sRGB color or colors shape==... x 3 (sR, sG, and sB channels)
    :return: the luminance computed using the sRGB color
    """
    lRGB = np.zeros(shape=sRGB.shape)
    lRGB[sRGB <= 0.03928] = sRGB[sRGB <= 0.03928] / 12.92
    lRGB[sRGB > 0.03928] = ((sRGB[sRGB > 0.03928] + 0.055) / 1.055) ** 2.4
    luminance = 0.2126 * lRGB[...,0] + 0.7152 * lRGB[...,1] + 0.0722 * lRGB[...,2]
    return luminance


def contrast_ratio(color1, color2):
    """
    Compute the contrast ratio between two 24-bits RGB colors in range [0, 255]
    see https://www.w3.org/TR/2008/REC-WCAG20-20081211/#contrast-ratiodef for more references
    :param color1: one of the 24-bits RGB colors in range [0, 255]
    :param color2: one of the 24-bits RGB colors in range [0, 255]
    :return: the contrast ratio between two 24-bits RGB colors. Contrast ratio >= 1
    """
    luminance1 = _sRGB2luminance(_RGB2sRGB(color1))
    luminance2 = _sRGB2luminance(_RGB2sRGB(color2))
    ratio = (luminance1 + 0.05) / (luminance2 + 0.05)
    if ratio < 1:
        ratio = 1 / ratio
    return ratio


def grabcut_foreback_segmentation(image, start_row=0, start_col=0, row_size=-1, col_size=-1, num_iter=3):
    """
    Perform the GrabCut segmentation over the input image with a rectangle of possible foreground
    specified by user. The GrabCut segment the image into two parts foreground and background, and
    the function return the 1D image of the foreground and background as the output
    :param image: The input image for GrabCut segmentation
    :param start_row: The starting row of the foreground rectangle of possible foreground
    :param start_col: The starting col of the foreground rectangle of possible foreground
    :param row_size: The vertical length of the rectangle
    :param col_size: The horizontal length of the rectangle
    :param num_iter: The number of iterations for GrabCut to run
    :return: 1D image of the foreground part of the image, and 1D image of the background part of the image
    Expected shape== Number of pixels x channels
    """

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
    # The obvious foreground and probable foreground are marked with 1 and 3
    foreground_image = image[np.where((mask == 1) | (mask == 3))]
    # The obvious background and probable background are marked with 0 and 2
    background_image = image[np.where((mask == 0) | (mask == 2))]

    return foreground_image, background_image


def write_in_info(info_row, file_name="output.csv", mode='a'):
    """
    Write a row of information to the csv file with a python list (not numpy array).
    All the values in numpy array (such as colors) are recommended to be converted to the list
    before write into the info_row.
    :param mode: The mode for using the file
    :param info_row: A row of data that will be write to the target csv file
    :param file_name: The name of the csv file
    """
    with open(file_name, newline="", mode=mode) as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(info_row)

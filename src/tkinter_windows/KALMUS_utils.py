import cv2
import src.measure_utils  as measure_utils


def compare_two_barcodes(barcode_1, barcode_2):
    target_barcode_1 = barcode_1.get_barcode().astype("float64")
    target_barcode_2 = barcode_2.get_barcode().astype("float64")
    if target_barcode_1.size <= target_barcode_2.size:
        target_barcode_1 = cv2.resize(target_barcode_1, dsize=target_barcode_2.shape[:2][::-1],
                                      interpolation=cv2.INTER_NEAREST)
    elif target_barcode_1.size > target_barcode_2.size:
        target_barcode_2 = cv2.resize(target_barcode_2, dsize=target_barcode_1.shape[:2][::-1],
                                      interpolation=cv2.INTER_NEAREST)

    cross_corre = measure_utils.cross_correlation(target_barcode_1.astype("float64"),
                                                  target_barcode_2.astype("float64"))
    loc_cross_corre = measure_utils.local_cross_correlation(target_barcode_1.astype("float64"),
                                                            target_barcode_2.astype("float64"))
    nrmse = measure_utils.nrmse_similarity(target_barcode_1.astype("float64"),
                                           target_barcode_2.astype("float64"))
    mse = measure_utils.ssim_similarity(target_barcode_1.astype("float64"),
                                        target_barcode_2.astype("float64"))

    colors_barcode_1 = barcode_1.colors
    colors_barcode_2 = barcode_2.colors

    if colors_barcode_1.shape[0] > colors_barcode_2.shape[0]:
        colors_barcode_1 = colors_barcode_1[measure_utils.get_resample_index(len(colors_barcode_1),
                                                                             len(colors_barcode_2))]
    elif colors_barcode_1.shape[0] < colors_barcode_2.shape[0]:
        colors_barcode_2 = colors_barcode_2[measure_utils.get_resample_index(len(colors_barcode_2),
                                                                             len(colors_barcode_1))]

    hue_string_1 = measure_utils.generate_hue_strings_from_color_barcode(colors_barcode_1)
    hue_string_2 = measure_utils.generate_hue_strings_from_color_barcode(colors_barcode_2)

    needleman = measure_utils.compare_needleman_wunsch(hue_string_1, hue_string_2, normalized=True)
    smithw = measure_utils.compare_smith_waterman(hue_string_1, hue_string_2, normalized=True)

    return cross_corre, loc_cross_corre, nrmse, mse, needleman, smithw


def get_comparison_result_text(barcode_1, barcode_2):
    cross_corre, loc_cross_corre, nrmse, ssim, needleman, smith = compare_two_barcodes(barcode_1, barcode_2)

    result_text = "Comparison metrics:\n" \
                  "NRMSE Similarity:                  {:10.4f}\n" \
                  "SSIM Similarity:                     {:10.4f}\n" \
                  "Cross Correlation:                 {:10.4f}\n" \
                  "Local Cross Correlation:         {:10.4f}\n" \
                  "Needleman Wunsch Similarity:{:10.4f}\n" \
                  "Smith Waterman Similarity:     {:10.4f}".format(nrmse, ssim, cross_corre, loc_cross_corre,
                                                                   needleman, smith)
    return result_text

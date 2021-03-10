from kalmus.barcodes.BarcodeGenerator import BarcodeGenerator
import argparse
import sys


def parse_args_into_dict(args):
    ap = argparse.ArgumentParser(description="Command line Barcode generator")
    # Video path
    ap.add_argument("-p", "--path", required=True, type=str, help="Path to the video")

    # Color metric
    ap.add_argument("--color_metric", required=True, type=str,
                    help="Color metric. available options: [Average, Median, Mode, Top-dominant, Weighted-dominant, "
                         "Brightest, Bright]")

    # Frame type
    ap.add_argument("--frame_type", required=True, type=str,
                    help="Type of the frame sampling. available options: [Whole_frame, High_contrast_region, "
                         "High_contrast_region, Low_contrast region, Foreground, Background]")

    # Barcode type
    ap.add_argument("--barcode_type", required=True, type=str,
                    help="Type of the generated barcode. available options: [Color, Brightness]")

    # Skip over how many frames after collecting colors/brightness
    ap.add_argument("--skip", required=False, type=int, help="Skip number of frames before collecting colors",
                    default=0)

    # Sampled frame rate
    ap.add_argument("-s", "--step", required=True, type=int, help="Sampled frame rate",
                    default=1)

    # Total frames in barcode
    ap.add_argument("-t", "--total_frames", required=False, type=int,
                    help="Total number of frames to be collected from the input video into the barcode",
                    default=1e8)

    # Total frames in barcode
    ap.add_argument("--num_thread", required=False, type=int,
                    help="Number of threads used to generate barcode. Single by default.",
                    default=None)
    # Total frames in barcode
    ap.add_argument("--saved_frame_rate", required=False, type=float,
                    help="Saved one frame every saved_frame_rate seconds. No frames saved during generation "
                         "by default",
                    default=None)
    # Rescale frame in generation
    ap.add_argument("--rescale_frame_factor", required=False, type=float,
                    help="Factor that frame will be resized during the generation. Frame is not resized by default",
                    default=-1)
    # Total frames in barcode
    ap.add_argument("-o", "--output_path", required=False, type=str,
                    help="Path to the output JSON barcode. By default, path==saved_{barcode_type}_{frame_type}_"
                         "{color_metric}.json",
                    default=None)
    return vars(ap.parse_args(args))


def main(args=sys.argv[1:]):
    args = parse_args_into_dict(args=args)

    if args["saved_frame_rate"] is None:
        saved_frame_in_generation = False
    else:
        saved_frame_in_generation = True
    barcode_generator = BarcodeGenerator(frame_type=args["frame_type"], color_metric=args["color_metric"],
                                         barcode_type=args["barcode_type"], sampled_frame_rate=args["step"],
                                         skip_over=args["skip"], total_frames=args["total_frames"])
    barcode_generator.generate_barcode(video_file_path=args["path"], num_thread=args["num_thread"],
                                       save_frames=saved_frame_in_generation, save_frames_rate=args["saved_frame_rate"],
                                       rescale_frames_factor=args["rescale_frame_factor"])
    barcode = barcode_generator.get_barcode()
    barcode.save_as_json(filename=args["output_path"])

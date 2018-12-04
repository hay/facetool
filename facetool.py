#!/usr/bin/env python3
from facetool import media, Swapper, util, Poser, Detect, Path, config, Profiler
import facetool
import argparse
import logging
import json
import os
import pdb
from tqdm import tqdm

COMMANDS = (
    "combineframes",
    "count",
    "crop",
    "extractframes",
    "locate",
    "pose",
    "probe",
    "swap",
)

logger = logging.getLogger(__name__)

# Note that we always profile, we just don't print the output if the
# option is not enabled
profiler = Profiler("facetool.py")

def get_parser():
    parser = argparse.ArgumentParser(description = "Manipulate faces in videos and images")

    # Essentials
    parser.add_argument("command", choices = COMMANDS, nargs = "?")
    parser.add_argument("-i", "--input", type = str,
        required = True,
        help = "Input file or folder, 'face' when swapping"
    )
    parser.add_argument("-o", "--output", type = str,
        help = "Output file or folder",
        default = None
    )
    parser.add_argument("-t", "--target", type = str,
        help = "'Head' when swapping"
    )

    # Extra arguments
    parser.add_argument("-bl", "--blur", type = float,
        default = facetool.BLUR_AMOUNT,
        help = "Amount of blur to use during colour correction"
    )
    parser.add_argument("-fr", "--framerate", type = str,
        default = facetool.DEFAULT_FRAMERATE
    )
    parser.add_argument("-fa", "--feather", type = int,
        default = facetool.FEATHER_AMOUNT,
        help = "Softness of edges on a swapped face"
    )
    parser.add_argument("-kt", "--keep-temp", action = "store_true",
        help = "Keep temporary files (used with video swapping"
    )
    parser.add_argument("--no-eyesbrows", action = "store_true")
    parser.add_argument("--no-nosemouth", action = "store_true")
    parser.add_argument("-pp", "--predictor-path", type = str,
        default = "./data/landmarks.dat"
    )
    parser.add_argument("--profile", action = "store_true",
        help = "Show profiler information"
    )
    parser.add_argument("-s", "--swap", action = "store_true",
        help = "Swap input and target"
    )
    parser.add_argument("-v", "--verbose", action = "store_true",
        help = "Show debug information"
    )
    parser.add_argument("-vv", "--extra-verbose", action = "store_true",
        help = "Show debug information AND raise / abort on exceptions"
    )

    return parser

def main(args):
    if args.verbose or args.extra_verbose:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(args)

    config.PROFILE = args.profile
    config.VERBOSE = args.verbose or args.extra_verbose

    # Swap around input and target
    if args.swap:
        args.input, args.target = args.target, args.input

    inp = Path(args.input)
    out = Path(args.output)
    target = Path(args.target)

    # Okay, the main stuff, get the command
    # Extract all frames from a movie to a set of jpg files
    if args.command == "extractframes":
        util.mkdir_if_not_exists(args.output)
        media.extractframes(args.input, args.output)

    # Combine all frames from a set of jpg files to a movie
    elif args.command == "combineframes":
        media.combineframes(args.input, args.output, framerate = args.framerate)

    # Show metadata on a media file
    elif args.command == "probe":
        data = media.probe(args.input)
        jsondata = json.dumps(data, indent = 4)
        print(jsondata)

    elif args.command == "pose":
        poser = Poser(predictor_path = args.predictor_path)
        poses = poser.get_poses(args.input, outpath = args.output)
        print(f"{args.input}: {poses}")

    elif args.command == "count":
        detect = Detect()

        for path in inp.files():
            count = detect.count(path)
            print(f"Number of faces in '{path}': {count}")

    elif args.command == "locate":
        detect = Detect()

        for path in inp.files():
            to_directory = os.path.isdir(args.input)
            locations = detect.locate(path, args.output, to_directory = to_directory)
            print(locations)

    elif args.command == "crop":
        detect = Detect()

        for path in inp.files():
            print(f"Cropping <{path}>")

            try:
                detect.crop(path, args.output)
            except Exception as e:
                util.handle_exception(e, reraise = args.extra_verbose)

    elif args.command == "swap":
        profiler.tick("start swapping")
        # First check if all arguments are given
        arguments = [args.input, args.target]

        if not all(arguments + [args.output]):
            raise Exception("Input, target and output are required for swapping")

        # And if these things are paths or files
        if not all([os.path.exists(a) for a in arguments]):
            raise Exception("Input and target should be valid files or directories")

        pbar = tqdm()

        def update_pbar():
            pbar.total = swapper.filecount
            pbar.update()

            if args.verbose:
                pbar.write(swapper.last_message)

        # That is out of the way, set up the swapper
        swapper = Swapper(
            predictor_path = args.predictor_path,
            feather = args.feather,
            blur = args.blur,
            reraise_exceptions = args.extra_verbose,
            keep_temp = args.keep_temp,
            overlay_eyesbrows = not args.no_eyesbrows,
            overlay_nosemouth = not args.no_nosemouth,
            reporthook = update_pbar
        )

        # Directory of faces to directory of heads
        if inp.is_dir() and target.is_dir():
            swapper.swap_directory_to_directory(inp, target, out)

        # Face to directory of heads
        elif media.is_image(args.input) and os.path.isdir(args.target):
            swapper.swap_image_to_directory(args.input, args.target, args.output)

        # Directory of faces to head
        elif os.path.isdir(args.input) and media.is_image(args.target):
            swapper.swap_directory_to_image(args.input, args.target, args.output)

        # Face in image to video
        elif media.is_video(args.target) and media.is_image(args.input):
            swapper.swap_image_to_video(args.target, args.input, args.output)

        # Face of video to head in other video
        elif media.is_video(args.target) and media.is_video(args.input):
            swapper.swap_video_to_video(args.target, args.input, args.output)

        # Image to image
        elif media.is_image(args.target) and media.is_image(args.input):
            swapper.swap_image_to_image(args.target, args.input, args.output)

        # I don't even know if there is an option that isn't in the list above,
        # but if it isn't, you'll get this
        else:
            raise Exception("Invalid swap options")

        pbar.close()
        profiler.tick("done swapping")
    else:
        # No arguments, just display help
        parser.print_help()

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    try:
        main(args)
    except Exception as e:
        util.handle_exception(e, reraise = args.extra_verbose)

    if config.PROFILE:
        profiler.dump_events()
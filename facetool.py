#!/usr/bin/env python3
from facetool import media, Swapper, util, DEFAULT_FRAMERATE, FEATHER_AMOUNT, BLUR_AMOUNT
import argparse
import logging
import json
import os

COMMANDS = ("swap", "extractframes", "combineframes", "probe")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description = "Manipulate faces in videos and images")

    # Essentials
    parser.add_argument("command", choices = COMMANDS, nargs = "?")
    parser.add_argument("-i", "--input", type = str, required = True)
    parser.add_argument("-o", "--output", type = str)
    parser.add_argument("-t", "--target", type = str)

    # Extra arguments
    parser.add_argument("-bl", "--blur", type = float, default = BLUR_AMOUNT,
        help = "Amount of blur to use during colour correction, as a fraction of the pupillary distance."
    )
    parser.add_argument("-f", "--framerate", type = str, default = DEFAULT_FRAMERATE)
    parser.add_argument("-fa", "--feather", type = int, default = FEATHER_AMOUNT, help = "Softness of edges on a swapped face")
    parser.add_argument("-kt", "--keep-temp", action = "store_true", help = "Keep temporary files (used with video swapping")
    parser.add_argument("-pp", "--predictor-path", type = str, default = "./data/landmarks.dat")
    parser.add_argument("-s", "--swap", action = "store_true", help = "Swap input and target")
    parser.add_argument("-v", "--verbose", action = "store_true")
    parser.add_argument("-vv", "--extra-verbose", action = "store_true")

    args = parser.parse_args()

    if args.verbose or args.extra_verbose:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(args)

    # Swap around input and target
    if args.swap:
        args.input, args.target = args.target, args.input

    if args.command == "extractframes":
        util.mkdir_if_not_exists(args.output)
        media.extractframes(args.input, args.output)
    elif args.command == "combineframes":
        media.combineframes(args.input, args.output, framerate = args.framerate)
    elif args.command == "probe":
        data = media.probe(args.input)
        jsondata = json.dumps(data, indent = 4)
        print(jsondata)
    elif args.command == "swap":
        swapper = Swapper(
            predictor_path = args.predictor_path,
            feather = args.feather,
            blur = args.blur,
            raise_exceptions = args.extra_verbose,
            keep_temp = args.keep_temp
        )

        arguments = [args.input, args.target, args.output]

        # First check if all arguments are given
        if not all(arguments):
            raise Exception("Input, target and output are required for swapping")

        # And if these things are paths or files
        if not all([os.path.exists(a) for a in arguments]):
            raise Exception("Input, target and output should all be valid files or directories")

        # Face to directory of heads
        if media.is_image(args.input) and os.path.isdir(args.target):
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
    else:
        # No arguments, just display help
        parser.print_help()

if __name__ == "__main__":
    main()
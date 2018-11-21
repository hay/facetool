#!/usr/bin/env python3
from facetool import media, Swapper, util, DEFAULT_FRAMERATE
import argparse
import logging
import json
import os

COMMANDS = ("swap", "extractframes", "combineframes", "probe")
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description = "Manipulate faces in videos and images")

# Essentials
parser.add_argument("command", choices = COMMANDS, nargs = "?")
parser.add_argument("-i", "--input", type = str, required = True)
parser.add_argument("-o", "--output", type = str)
parser.add_argument("-t", "--target", type = str)

# Extra arguments
parser.add_argument("-f", "--framerate", type = str, default = DEFAULT_FRAMERATE)
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
        args.predictor_path,
        raise_exceptions = args.extra_verbose,
        keep_temp = args.keep_temp
    )

    if not all([args.input, args.target, args.output]):
        raise Exception("Input, target and output are required for swapping")

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
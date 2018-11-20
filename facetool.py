#!/usr/bin/env python3
from facetool import media, swap
import argparse
import logging
import json
import os

DEFAULT_FRAMERATE = 30
COMMANDS = ("swap", "extractframes", "combineframes", "probe")
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description = "Manipulate faces in videos and images")
parser.add_argument("command", choices = COMMANDS, nargs = "?")
parser.add_argument("-i", "--input", type = str, required = True)
parser.add_argument("-o", "--output", type = str)
parser.add_argument("-t", "--target", type = str)
parser.add_argument("-f", "--framerate", type = str, default = DEFAULT_FRAMERATE)
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

logging.debug(args)

if args.command == "extractframes":
    if not os.path.isdir(args.output):
        logging.info(f"{args.output} does not exist, creating")
        os.mkdir(args.output)

    media.extractframes(args.input, args.output)
elif args.command == "combineframes":
    media.combineframes(args.input, args.output, framerate = args.framerate)
elif args.command == "probe":
    data = media.probe(args.input)
    jsondata = json.dumps(data, indent = 4)
    print(jsondata)
else:
    parser.print_help()
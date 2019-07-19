from collections import namedtuple
from glob import glob
from random import random

import logging
import os
import shutil
import sys

from facetool import config
from facetool.path import Path

logger = logging.getLogger(__name__)

Coord = namedtuple("Coord", "x y w h")
Point = namedtuple("Point", "x y")

def message(*args):
    if not config.QUIET:
        print(*args)

def mkdir_if_not_exists(path):
    if not os.path.isdir(path):
        logging.info(f"{path} does not exist, creating")
        os.mkdir(path)

def force_mkdir(paths):
    if not isinstance(paths, list):
        paths = [paths]

    for path in paths:
        if os.path.isdir(path):
            logger.debug(f"'{path}' exists, removing")
            shutil.rmtree(path)

        logger.debug(f"Creating directory '{path}'")
        os.mkdir(path)

def get_basename(filename):
    return os.path.splitext(os.path.basename(filename))[0]

# Return an iterator with all the files in a path, whether
# it is a file or a folder
def globify(path):
    if os.path.isfile(path):
        yield path
    else:
        files = glob(path + "/*")
        files = sorted(list(files))

        for f in files:
            yield f

def numberize_files(path):
    files = sorted(list(glob(path + "/*")))

    for index, oldpath in enumerate(files):
        newpath = f"{path}/{str(index).zfill(4)}.jpg"
        logger.debug(f"Renaming {oldpath} to {newpath}")
        os.rename(oldpath, newpath)

def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    # return a tuple of (x, y, w, h)
    return Coord(x, y, w, h)

def sample_remove(in_path, percentage, force_delete = False):
    if not force_delete:
        choice = input(f"This will REMOVE {round(percentage * 100)}% of all files, are you sure? [y/n] ")

        if choice.lower() != "y":
            sys.exit("Aborting sample")

    images = list(Path(in_path).images())
    logging.info(f"Removing {round(len(images) * percentage)} of {len(images)} images")

    for path in images:
        if random() < percentage:
            logging.debug(f"Removing {path}")
            path.unlink()
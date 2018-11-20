import os
import shutil
import logging
from glob import glob
logger = logging.getLogger(__name__)

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

def numberize_files(path):
    files = sorted(list(glob(path + "/*")))

    for index, oldpath in enumerate(files):
        newpath = f"{path}/{str(index).zfill(4)}.jpg"
        logger.debug(f"Renaming {oldpath} to {newpath}")
        os.rename(oldpath, newpath)
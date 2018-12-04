import os
import shutil
import logging
from . import config
from glob import glob
logger = logging.getLogger(__name__)

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

def handle_exception(e, reraise = False):
    if reraise:
        raise(e)
    else:
        msg = str(e)

        if not msg:
            msg = e.__class__.__name__

        if config.VERBOSE:
            print(f"Error: {msg}")

def numberize_files(path):
    files = sorted(list(glob(path + "/*")))

    for index, oldpath in enumerate(files):
        newpath = f"{path}/{str(index).zfill(4)}.jpg"
        logger.debug(f"Renaming {oldpath} to {newpath}")
        os.rename(oldpath, newpath)
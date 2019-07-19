# Cheers < https://stackoverflow.com/a/34116756/152809 >
import os
import logging
import pathlib
from .constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from .util import ArgumentError

logger = logging.getLogger(__name__)

class Path(type(pathlib.Path())):
    def could_be_dir(self):
        return self.suffix == "" and not self.is_dir()

    def count_images(self):
        return len(list(self.images()))

    def files(self):
        if not self.exists():
            raise ArgumentError(f"Path doesn't exist: {self}")
        elif self.is_file():
            yield Path(str(self))
        else:
            for path in self.glob("*"):
                yield path

    def images(self):
        for path in self.files():
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                yield path

    # FIXME: these functions are *really* quick and dirty
    def is_image(self):
        return self.suffix.lower() in IMAGE_EXTENSIONS

    def is_video(self):
        return self.suffix.lower() in VIDEO_EXTENSIONS

    def mkdir_if_not_exists(self):
        if not self.is_dir():
            logging.info(f"{self} does not exist, creating")
            os.mkdir(str(self))

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        if encoding is None and 'b' not in mode:
            encoding = 'utf-8'

        return super().open(mode, buffering, encoding, errors, newline)
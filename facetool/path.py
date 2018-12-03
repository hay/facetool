# Cheers < https://stackoverflow.com/a/34116756/152809 >
import pathlib
from .constants import IMAGE_EXTENSIONS

class Path(type(pathlib.Path())):
    def filecount(self):
        return len(list(self.glob("*")))

    def images(self):
        for path in self.glob("*"):
            if path.suffix in IMAGE_EXTENSIONS:
                yield path

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        if encoding is None and 'b' not in mode:
            encoding = 'utf-8'

        return super().open(mode, buffering, encoding, errors, newline)
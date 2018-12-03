import os
import logging
from glob import glob

logger = logging.getLogger(__name__)

class Path:
    def __init__(self, path):
        self._path = path

        if self._path:
            self.is_file = os.path.isfile(self._path)
            self.is_dir = os.path.isdir(self._path)
            self.basename = os.path.splitext(os.path.basename(self._path))[0]

    def files(self):
        if self.is_file:
            yield self._path
        else:
            files = glob(path + "/*")
            files = sorted(list(files))

            for f in files:
                yield f

    def __repr__(self):
        return self._path

    def __str__(self):
        return self._path
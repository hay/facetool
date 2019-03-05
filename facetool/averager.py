import logging
from .path import Path
from .detect import Detect

logger = logging.getLogger(__name__)

class Averager:
    def __init__(self):
        self.detector = Detect()

    def average(self, input_dir, output_file):
        if not Path(input_dir).is_dir():
            raise Exception("Input for averaging faces should be a directory")

        for img in Path(input_dir).images():
            print(img)
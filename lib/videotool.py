import logging
logger = logging.getLogger(__name__)

class Videotool:
    def __init__(self, inp, out, verbose = False):
        self.input = inp
        self.output = out

        if verbose:
            logging.basicConfig(level=logging.DEBUG)

    def combineframes(self):
        pass

    def extractframes(self):
        pass
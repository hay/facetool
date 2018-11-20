from glob import glob
import ffmpeg
import os
import logging

logger = logging.getLogger(__name__)

FRAME_FILENAME_LENGTH = 4

class Videotool:
    def __init__(
        self, inp, framerate, out = "out.mp4", verbose = False
    ):
        if not inp:
            raise Exception("Input is required")

        self.input = inp
        self.output = out
        self.framerate = framerate

        if verbose:
            logging.basicConfig(level=logging.DEBUG)

    def _getwh(self, path):
        data = self.probe(path)
        width = data["streams"][0]["width"]
        height = data["streams"][0]["height"]
        wh = f"{width}x{height}"
        return wh

    def _run(self, cmd):
        command = " ".join(cmd.compile())
        logging.debug(command)
        cmd.run()

    """
    Does something like this:

    ffmpeg -r 24.89 -f image2 -s 480x360 -i "video-in/%04d.jpg" -vcodec libx264 -crf 25 -pix_fmt yuv420p movie.mp4

    """
    def combineframes(self):
        inp = self.input

        if os.path.isdir(self.input):
            inp = f"{inp}/%04d.jpg"

        # Use the first file to get wh
        first_file = list(glob(f"{self.input}/*"))[0]
        wh = self._getwh(first_file)

        cmd = ffmpeg.input(inp,
            r = self.framerate,
            f = "image2",
            s = wh
        ).output(self.output,
            vcodec = "libx264",
            crf = "25",
            pix_fmt = "yuv420p"
        )

        self._run(cmd)

    def extractframes(self):
        data = self.probe()
        # framecount = data["streams"][0]["nb_frames"]
        # framelength = len(framecount)
        framelength = FRAME_FILENAME_LENGTH # Keep it simple for now
        output = f"{self.output}/%{framelength}d.jpg"
        cmd = ffmpeg.input(self.input).output(output, **{"q:v" : 2})

        self._run(cmd)

    def probe(self, inp = None):
        if not inp:
            inp = self.input

        return ffmpeg.probe(inp)
from glob import glob
from pathlib import Path
from .constants import DEFAULT_FRAMERATE, TEMP_AUDIO_FILENAME
from .command import Command
import ffmpeg
import os
import logging

logger = logging.getLogger(__name__)

FRAME_FILENAME_LENGTH = 4

def _getwh(path):
    data = probe(path)
    width = data["streams"][0]["width"]
    height = data["streams"][0]["height"]
    wh = f"{width}x{height}"
    return wh

def _run(cmd):
    command = " ".join(cmd.compile())
    logging.debug(command)
    cmd.run()

"""
Does something like this:

ffmpeg -i a.mp4 -i a.wav -c copy -map 0:v:0 -map 1:a:0 -shortest -c:a aac -b:a 192k b.mp4
"""
def combineaudio(inp, audio, out):
    logging.debug(f"Combining audio '{audio}' to '{inp}' as '{out}'")
    cmd_str = f"ffmpeg -i {inp} -i {audio} -c copy -map 0:v:0 -map 1:a:0 -shortest -c:a aac -b:a 192k {out}"

    # FIXME and use ffmpeg instead of command
    cmd = Command()
    cmd.call(cmd_str)

"""
Does something like this:

ffmpeg -r 24.89 -f image2 -s 480x360 -i "video-in/%04d.jpg" -vcodec libx264 -crf 25 -pix_fmt yuv420p movie.mp4

"""
def combineframes(inp, out, framerate = DEFAULT_FRAMERATE):
    if os.path.isdir(inp):
        path = f"{inp}/%04d.jpg"

    # Use the first file to get wh
    first_file = list(glob(f"{inp}/*"))[0]
    wh = _getwh(first_file)

    cmd = ffmpeg.input(path,
        r = framerate,
        f = "image2",
        s = wh
    ).output(out,
        vcodec = "libx264",
        crf = "25",
        pix_fmt = "yuv420p"
    )

    _run(cmd)

def extractaudio(inp, out):
    # Extract audio as a WAV, because re-adding it as MP3 somehow
    # doesn't work
    cmd = ffmpeg.input(inp).output(f"{out}/{TEMP_AUDIO_FILENAME}")
    _run(cmd)

def extractframes(inp, out):
    data = probe(inp)
    output = f"{out}/%{FRAME_FILENAME_LENGTH}d.jpg"
    cmd = ffmpeg.input(inp).output(output, **{"q:v" : 2})
    _run(cmd)

def is_image(inp):
    if not os.path.isfile(inp):
        return False

    data = probe(inp)
    return data["format"]["format_name"] == "image2"

# FIXME: this is obviously pretty ugly
def is_video(inp):
    return not is_image(inp)

def probe(inp = None):
    return ffmpeg.probe(inp)
import logging
import shutil
from glob import glob
from .path import Path

from .constants import FEATHER_AMOUNT, BLUR_AMOUNT
from .faceswap import Faceswap
from .media import is_image, is_video, extractframes, combineframes
from .util import force_mkdir, get_basename, numberize_files, mkdir_if_not_exists, handle_exception

logger = logging.getLogger(__name__)

HEAD_TMP = "head-tmp"
FACE_TMP = "face-tmp"
OUT_TMP = "out-tmp"
IMG_TO_VIDEO = (HEAD_TMP, OUT_TMP)
VIDEO_TO_VIDEO = (HEAD_TMP, OUT_TMP, FACE_TMP)

class Swapper:
    def __init__(self,
        predictor_path,
        blur = BLUR_AMOUNT,
        feather = FEATHER_AMOUNT,
        keep_temp = False,
        reraise_exceptions = False,
        overlay_eyesbrows = True,
        overlay_nosemouth = True,
        reporthook = None

    ):
        self.done = 0
        self.filecount = None
        self.last_message = None
        self.predictor_path = predictor_path
        self.keep_temp = keep_temp
        self.blur = blur
        self.feather = feather
        self.reraise_exceptions = reraise_exceptions
        self.reporthook = reporthook
        self.swap = Faceswap(
            predictor_path = self.predictor_path,
            feather = self.feather,
            blur = self.blur,
            overlay_eyesbrows = overlay_eyesbrows,
            overlay_nosemouth = overlay_nosemouth,
        )

    # FIXME: this swap parameter is *really* confusing, let's fix that at
    # a later time
    def _dirswap(self, image, directory, output_directory, swap = False):
        logging.debug(f"Directory swapping: {image} to all files in {directory} to {output_directory}")
        mkdir_if_not_exists(output_directory)
        image_base = get_basename(image)
        dirpath = Path(directory)
        self.filecount = dirpath.count_images()

        for path in dirpath.images():
            basename = get_basename(path)
            outpath = f"{output_directory}/{image_base}-{basename}.jpg"

            if swap:
                self._faceswap(path, image, outpath)
            else:
                self._faceswap(image, path, outpath)

    def _faceswap(self, head, face, out):
        msg = f"Faceswapping {face} on {head}, saving to {out}"
        self.last_message = msg

        try:
            self.swap.faceswap(head = str(head), face = str(face), output = str(out))
            self.done = self.done + 1
        except Exception as e:
            handle_exception(e, reraise = self.reraise_exceptions)

        if self.reporthook:
            self.reporthook()

    def swap_directory_to_image(self, directory, image, out):
        logging.debug(f"Dir to image: faces of {directory} to {image}")
        self._dirswap(image, directory, out)

    def swap_image_to_directory(self, image, directory, out):
        logging.debug(f"Image to dir: face of {image} to {directory}")
        self._dirswap(image, directory, out, swap = True)

    def swap_image_to_image(self, head, face, out):
        self.filecount = 1
        self._faceswap(head, face, out)

    def swap_image_to_video(self, head, face, out):
        [force_mkdir(p) for p in IMG_TO_VIDEO]
        extractframes(head, HEAD_TMP)
        dirpath = Path(HEAD_TMP)
        self.filecount = len(dirpath.glob("*"))

        for path in dirpath.glob("*"):
            outpath = f"{OUT_TMP}/{get_basename(path)}.jpg"
            self._faceswap(path, face, outpath)

        numberize_files(OUT_TMP)
        combineframes(OUT_TMP, out)

        if not self.keep_temp:
            [shutil.rmtree(p) for p in IMG_TO_VIDEO]

    def swap_video_to_video(self, head, face, out):
        [force_mkdir(p) for p in VIDEO_TO_VIDEO]
        extractframes(head, HEAD_TMP)
        extractframes(face, FACE_TMP)

        heads = sorted(glob(f"{HEAD_TMP}/*"))
        faces = sorted(glob(f"{FACE_TMP}/*"))

        if len(heads) != len(faces):
            logging.warning("Not the same amount of files in heads and faces")

        self.filecount = len(heads)

        for index, path in enumerate(heads):
            outpath = f"{OUT_TMP}/{get_basename(path)}.jpg"

            # Check if there is face, and if not, abort mission
            if index > len(faces) - 1:
                logging.warning("Not enough faces, aborting conversion")
                break

            face = faces[index]
            self._faceswap(path, face, outpath)

        numberize_files(OUT_TMP)
        combineframes(OUT_TMP, out)

        if not self.keep_temp:
            [shutil.rmtree(p) for p in VIDEO_TO_VIDEO]
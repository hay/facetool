import logging
import shutil
from glob import glob

from .faceswap import Faceswap
from .media import is_image, is_video, extractframes, combineframes
from .util import force_mkdir, get_basename, numberize_files

logger = logging.getLogger(__name__)

HEAD_TMP = "head-tmp"
FACE_TMP = "face-tmp"
OUT_TMP = "out-tmp"
IMG_TO_VIDEO = (HEAD_TMP, OUT_TMP)
VIDEO_TO_VIDEO = (HEAD_TMP, OUT_TMP, FACE_TMP)

class Swapper:
    def __init__(self, predictor_path, raise_exceptions = False, keep_temp = False):
        self.predictor_path = predictor_path
        self.raise_exceptions = raise_exceptions
        self.keep_temp = keep_temp
        self.swap = Faceswap(self.predictor_path)

    def _faceswap(self, head, face, out):
        logger.debug(f"Processing {head} -> {face}")

        try:
            self.swap.faceswap(head = head, face = face, output = out)
        except Exception as e:
            if self.raise_exceptions:
                raise(e)

            logger.debug(e)
            logger.error("Couldn't convert this face")

    def swap_image_to_image(self, head, face, out):
        self._faceswap(head, face, out)

    def swap_image_to_video(self, head, face, out):
        [force_mkdir(p) for p in IMG_TO_VIDEO]
        extractframes(head, HEAD_TMP)

        for path in glob(f"{HEAD_TMP}/*"):
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
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from .path import Path
from .constants import FEATHER_AMOUNT, BLUR_AMOUNT, TEMP_AUDIO_FILENAME
from .media import is_image, is_video, extractframes, combineframes, extractaudio, combineaudio
from .util import force_mkdir, get_basename, numberize_files, mkdir_if_not_exists, message
from .errors import TooManyFacesError, NoFacesError, FaceError

logger = logging.getLogger(__name__)

AUDIO_TMP = "audio-tmp"
HEAD_TMP = "head-tmp"
FACE_TMP = "face-tmp"
OUT_TMP = "out-tmp"
IMG_TO_VIDEO = (HEAD_TMP, OUT_TMP)
VIDEO_TO_VIDEO = (HEAD_TMP, OUT_TMP, FACE_TMP, AUDIO_TMP)

def parse_swap_order(swap_order):
    if swap_order == None:
        return None

    order = []

    for item in swap_order.split(","):
        if item == "x":
            order.append(-1)
        else:
            order.append(int(item))

    return order

class Swapper:
    def __init__(self,
        predictor_path,
        blur = BLUR_AMOUNT,
        feather = FEATHER_AMOUNT,
        keep_temp = False,
        overlay_eyesbrows = True,
        overlay_nosemouth = True,
        only_mouth = False,
        swap_audio = True,
        audio_input = False,
        reporthook = None,
        swap_method = "faceswap",
        warp_3d = False,
        swap_order = None,
        swap_order_repeat = False,
        concurrent = False
    ):
        self.done = 0
        self.filecount = None
        self.last_message = None
        self.predictor_path = predictor_path
        self.keep_temp = keep_temp
        self.blur = blur
        self.feather = feather
        self.reporthook = reporthook
        self.swap_method = swap_method
        self.warp_3d = warp_3d
        self.swap_order = parse_swap_order(swap_order)
        self.swap_order_repeat = swap_order_repeat
        self.swap_audio = swap_audio
        self.audio_input = audio_input
        self.concurrent = concurrent

        kwargs = {
            "predictor_path" : self.predictor_path,
            "feather" : self.feather,
            "blur" : self.blur,
            "overlay_eyesbrows" : overlay_eyesbrows,
            "overlay_nosemouth" : overlay_nosemouth,
            "only_mouth" : only_mouth
        }

        logging.debug(f"Using swapmethod '{self.swap_method}'")

        if self.swap_method == "faceswap":
            from .faceswap import Faceswap
            self.swap = Faceswap(**kwargs)
        elif self.swap_method == "faceswap3d":
            from .faceswap3d import Faceswap3d
            kwargs["warp_3d"] = self.warp_3d
            self.swap = Faceswap3d(**kwargs)

    # FIXME: this swap parameter is *really* confusing, let's fix that at
    # a later time
    def _dirswap(self, image, directory, output_directory, swap = False):
        logging.debug(f"Directory swapping: {image} to all files in {directory} to {output_directory}")
        mkdir_if_not_exists(output_directory)
        image_base = get_basename(image)
        dirpath = Path(directory)
        self._set_filecount(dirpath.count_images())

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
            self.swap.faceswap(
                head = str(head),
                face = str(face),
                output = str(out),
                order = self.swap_order,
                order_repeat = self.swap_order_repeat
            )
        except TooManyFacesError:
            message(f"Too many faces, could not swap ({msg})")
        except NoFacesError:
            message(f"No faces found, could not swap ({msg})")
        except IndexError as e:
            message(f"Index error: {e}, ({msg})")

        self.done = self.done + 1

        if self.reporthook:
            self.reporthook()

    # This is a wrapper so we can control multithreading
    def _multiswap(self, swaps):

        if self.concurrent:
            paths, faces, outpaths = zip(*swaps)

            with ThreadPoolExecutor(max_workers = 20) as executor:
                executor.map(self._faceswap, paths, faces, outpaths)
        else:
            # Simply iterate over the list instead of using the
            # threaded model
            [self._faceswap(*swap) for swap in swaps]

    def _set_filecount(self, filecount):
        if not self.filecount:
            self.filecount = filecount
        else:
            logging.debug("Already set filecount")

    def swap_directory_to_directory(self, face_dir, head_dir, out_dir):
        logging.debug(f"Dir to dir: faces in {face_dir} to heads in {head_dir} to {out_dir}")
        self._set_filecount(Path(face_dir).count_images() * Path(head_dir).count_images())

        for face in Path(face_dir).images():
            self.swap_image_to_directory(str(face), head_dir, out_dir)

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
        self._set_filecount(dirpath.count_images())

        swaps = []

        for path in dirpath.glob("*"):
            outpath = f"{OUT_TMP}/{get_basename(path)}.jpg"
            swaps.append([path, face, outpath])

        self._multiswap(swaps)

        numberize_files(OUT_TMP)
        combineframes(OUT_TMP, out)

        if not self.keep_temp:
            [shutil.rmtree(p) for p in IMG_TO_VIDEO]

    def swap_video_to_video(self, head, face, out):
        [force_mkdir(p) for p in VIDEO_TO_VIDEO]
        extractframes(head, HEAD_TMP)
        extractframes(face, FACE_TMP)
        extractaudio(face, AUDIO_TMP)

        heads = sorted(glob(f"{HEAD_TMP}/*"))
        faces = sorted(glob(f"{FACE_TMP}/*"))

        if len(heads) != len(faces):
            logging.warning("Not the same amount of files in heads and faces")

        self._set_filecount(len(heads))

        swaps = []

        for index, path in enumerate(heads):
            outpath = f"{OUT_TMP}/{get_basename(path)}.jpg"

            # Check if there is face, and if not, abort mission
            if index > len(faces) - 1:
                logging.warning("Not enough faces, aborting conversion")
                break

            face = faces[index]
            swaps.append([path, face, outpath])

        self._multiswap(swaps)

        numberize_files(OUT_TMP)

        if not self.swap_audio:
            combineframes(OUT_TMP, out)
        else:
            TMP_VIDEO = str(Path(OUT_TMP) / "_silent.mp4")

            # TODO: make a function out of this
            if self.audio_input:
                audio_file = args.audio_input
            else:
                audio_file = f"{AUDIO_TMP}/{TEMP_AUDIO_FILENAME}"

            combineframes(OUT_TMP, TMP_VIDEO)
            combineaudio(TMP_VIDEO, audio_file, out)

        if not self.keep_temp:
            [shutil.rmtree(p) for p in VIDEO_TO_VIDEO]
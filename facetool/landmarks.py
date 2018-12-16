from skimage import io
from .util import rect_to_bb, Point
import dlib
import logging
logger = logging.getLogger(__name__)

class Landmarks:
    def __init__(self, predictor_path, normalize_coords = True):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)
        self.normalize_coords = normalize_coords

    def _get_faces(self, image):
        logging.debug(f"Getting faces for {image}")
        img = io.imread(image)
        faces = self.detector(img)

        if len(faces) == 0:
            logging.debug(f"No faces in {image}")

        return len(faces), faces, img

    # Normalize points to a number between 0 - 1
    def _normalize(self, shape, face):
        box = rect_to_bb(face)

        def _coord(p):
            return Point(
                (p.x - box.x) / box.w,
                (p.y - box.y) / box.h
            )

        return [_coord(p) for p in shape]

    def get_landmarks(self, path):
        nr_of_faces, faces, img = self._get_faces(path)

        if nr_of_faces == 0:
            logging.debug(f"No faces found for {path}")
            return False

        # For now, we only deal with the first face with multiple faces
        if nr_of_faces > 1:
            logging.warning("Detected multiple faces, using the first one")

        face = faces[0]
        shape = self.predictor(img, face).parts()

        if self.normalize_coords:
            shape = self._normalize(shape, face)

        return shape
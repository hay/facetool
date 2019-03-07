import face_recognition
import json
import logging
import math
from .constants import DEFAULT_TRESHOLD
from .path import Path

logger = logging.getLogger(__name__)

class Recognizer:
    def __init__(self, treshold = DEFAULT_TRESHOLD):
        self.treshold = DEFAULT_TRESHOLD

    # From:
    # < https://github.com/ageitgey/face_recognition/wiki/Calculating-Accuracy-as-a-Percentage >
    def _face_distance_to_conf(self, face_distance):
        if face_distance > self.treshold:
            range_ = (1.0 - self.treshold)
            linear_val = (1.0 - face_distance) / (range_ * 2.0)
            return linear_val
        else:
            range_ = self.treshold
            linear_val = 1.0 - (face_distance / (range_ * 2.0))
            return linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))

    # Load one image, get the encoding and return that, but only if there
    # is exactly *one* face
    def _encoding_from_image(self, path):
        logging.debug(f"Getting encoding for {path}")
        image = face_recognition.load_image_file(path)
        image_encodings = face_recognition.face_encodings(image)

        if len(image_encodings) != 1:
            raise Exception(f"{path} has 0 or more than 1 face, skipping")

        return image_encodings[0]

    def encode_path(self, path):
        encodings = {}

        for image_path in Path(path).images():
            image_path = str(image_path)

            try:
                encoding = self._encoding_from_image(image_path)
            except:
                continue

            encodings[image_path] = encoding.tolist()

        # Return encodings in a key, for future-proofing this file format
        # And return as JSON
        return json.dumps({
            "encodings" : encodings
        })

    def recognize(self, input_path, target_path, as_percentage = False):
        # First get the encoding for the input image and check if we
        # have only one face
        logging.debug(f"Getting encoding for input image {input_path}")
        input_image = face_recognition.load_image_file(input_path)
        input_encoding = face_recognition.face_encodings(input_image)

        if len(input_encoding) != 1:
            raise Exception("Found more than one face in this image, aborting")
        else:
            # Take the first face
            input_encoding = input_encoding[0]

        # First get encodings from all images in the target path
        encodings = []

        image_paths = [str(p) for p in Path(target_path).images()]

        for imgpath in image_paths:
            try:
                encoding = self._encoding_from_image(imgpath)
            except:
                continue

            encodings.append(encoding)

        results = face_recognition.face_distance(encodings, input_encoding)

        if as_percentage:
            logging.debug("Converting all face distances to percentages")
            results = [self._face_distance_to_conf(d) for d in results]

        return dict(zip(image_paths, results))
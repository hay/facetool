import face_recognition
import logging
from .path import Path

logger = logging.getLogger(__name__)

class Recognizer:
    def __init__(self):
        pass

    def recognize(self, input_path, target_path):
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
            logging.debug(f"Getting encoding for {imgpath}")
            image = face_recognition.load_image_file(imgpath)
            image_encodings = face_recognition.face_encodings(image)

            if len(image_encodings) != 1:
                logging.debug(f"{imgpath} has 0 or more than 1 face, skipping")
                continue

            # Get the first encoding
            encodings.append(image_encodings[0])

        results = face_recognition.face_distance(encodings, input_encoding)

        return dict(zip(image_paths, results))
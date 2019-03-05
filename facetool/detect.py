# Based on https://gist.github.com/ageitgey/1c1cb1c60ace321868f7410d48c228e1

import dlib
import cv2
import logging
import os

from .util import get_basename, mkdir_if_not_exists
from skimage import io

logger = logging.getLogger(__name__)

class Detect:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()

    def _get_faces(self, image):
        logging.debug(f"Getting faces for {image}")
        img = io.imread(image)
        faces = self.detector(img)

        if len(faces) == 0:
            logging.debug(f"No faces in {image}")

        return faces

    def count(self, image):
        faces = self._get_faces(image)
        return len(faces)

    def crop(self, image, outpath):
        logging.debug(f"Cropping {image} to {outpath}")
        mkdir_if_not_exists(outpath)
        rects = self.locate(image)
        img = cv2.imread(image, cv2.IMREAD_COLOR)
        basename = get_basename(image)

        for index, rect in enumerate(rects):
            outfile = f"{outpath}/{basename}-{index}.jpg"
            x, y, x2, y2 = rect
            crop = img[y:y2, x:x2]
            cv2.imwrite(outfile, crop)
            logging.debug(f"Cropped to {outfile}")

    def locate(self, image, output = None, to_directory = None):
        faces = self._get_faces(image)
        rects = []

        if to_directory:
            mkdir_if_not_exists(output)

        logging.debug(f"Getting rects")

        for index, rect in enumerate(faces):
            rects.append([
                rect.left(),
                rect.top(),
                rect.right(),
                rect.bottom()
            ])

        if output:
            logging.debug(f"Writing bounding boxes to {output}")

            out = cv2.imread(str(image), cv2.IMREAD_COLOR)

            for rect in rects:
                logging.debug(f"Plotting rect: {rect}")
                x, y, x2, y2 = rect
                p1 = (x, y)
                p2 = (x2, y2)
                c = (255, 0, 0)
                logging.debug(f"{p1}, {p2}")
                cv2.rectangle(out, p1, p2, c, 5)

            # If output is a directory, generate a name based on the
            # input filename
            if to_directory:
                outpath = f"{output}/{get_basename(image)}-crop.jpg"
            else:
                outpath = output

            logging.debug(f"Writing to {outpath}")

            cv2.imwrite(outpath, out)

        return rects
# Based on https://gist.github.com/ageitgey/1c1cb1c60ace321868f7410d48c228e1

import dlib
import cv2
import logging

from skimage import io

logger = logging.getLogger(__name__)

class Detect:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()

    def _get_faces(self, image):
        logging.debug(f"Getting faces for {image}")
        img = io.imread(image)
        faces = self.detector(img)
        return faces

    def count(self, image):
        faces = self._get_faces(image)
        return len(faces)

    def locate(self, image, output = None):
        faces = self._get_faces(image)
        rects = []

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

            out = cv2.imread(image, cv2.IMREAD_COLOR)

            for rect in rects:
                logging.debug(f"Plotting rect: {rect}")
                x, y, x2, y2 = rect
                p1 = (x, y)
                p2 = (x2, y2)
                c = (255, 0, 0)
                logging.debug(f"{p1}, {p2}")
                cv2.rectangle(out, p1, p2, c, 5)

            cv2.imwrite(output, out)

        return rects
# Based on https://gist.github.com/ageitgey/1c1cb1c60ace321868f7410d48c228e1

import dlib
from skimage import io

class Detect:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()

    def _get_faces(self, image):
        img = io.imread(image)
        faces = self.detector(img)
        return faces

    def count(self, image):
        faces = self._get_faces(image)
        return len(faces)

    def locate(self, image):
        faces = self._get_faces(image)
        rects = []

        for index, rect in enumerate(faces):
            rects.append([
                rect.left(),
                rect.top(),
                rect.right(),
                rect.bottom()
            ])

        return rects

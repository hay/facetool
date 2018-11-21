import sys
import os
import dlib
import glob
import cv2
import numpy as np
import logging
from .facepose import detect_pose
from skimage import io

logger = logging.getLogger(__name__)

class Poser:
    def __init__(self, predictor_path):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)

    def get_poses(self,
        f, outpath = None, draw_points = True, draw_direction_line = True
    ):
        logger.debug(f"Processing file {f}")
        img = io.imread(f)
        out = cv2.imread(f, cv2.IMREAD_COLOR)

        detects = self.detector(img, 1)
        logger.debug(f"Number of faces detected: {len(detects)}")

        if len(detects) < 1:
            return False

        poses = []

        for k, d in enumerate(detects):
            shape = self.predictor(out, d).parts()

            pose = detect_pose(
                out,
                shape,
                draw_points = draw_points,
                draw_direction_line = draw_direction_line
            )

            poses.append(pose)

        if outpath:
            logger.debug(f"Writing to {outpath}")
            cv2.imwrite(outpath, out)

        return poses

if __name__ == "__main__":
    detect(sys.argv[1])
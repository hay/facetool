#!/usr/bin/env python3

import sys
import os
import dlib
import glob
import cv2
import numpy as np
from face_pose import detect_pose
from skimage import io

def detect(path):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("./landmarks.dat")

    for f in glob.glob(os.path.join(path, "*.jpg")):
        print("Processing file: {}".format(f))
        img = io.imread(f)
        out = cv2.imread(f, cv2.IMREAD_COLOR)

        detects = detector(img, 1)
        print("Number of faces detected: {}".format(len(detects)))

        if len(detects) < 1:
            continue

        for k, d in enumerate(detects):
            shape = predictor(out, d).parts()
            pose = detect_pose(out, shape, draw_points = True, draw_direction_line = True)
            print(pose)

        cv2.imwrite(f.replace(".jpg", "-mod.jpg"), out)

if __name__ == "__main__":
    detect(sys.argv[1])
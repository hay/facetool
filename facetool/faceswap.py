"""
Faceswap library

Based on http://matthewearl.github.io/2015/07/28/switching-eds-with-python/

Copyright (c) 2015 Matthew Earl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
    NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
    USE OR OTHER DEALINGS IN THE SOFTWARE.

This is the code behind the Switching Eds blog post:

    http://matthewearl.github.io/2015/07/28/switching-eds-with-python/

See the above for an explanation of the code below.

To run the script you'll need to install dlib (http://dlib.net) including its
Python bindings, and OpenCV. You'll also need to obtain the trained model from
sourceforge:

    http://sourceforge.net/projects/dclib/files/dlib/v18.10/shape_predictor_68_face_landmarks.dat.bz2

"""

from .constants import FEATHER_AMOUNT, BLUR_AMOUNT
from .profiler import Profiler
profiler = Profiler("faceswap.py")

import cv2
import dlib
import numpy
import sys
import os
import argparse
import logging
from . import config

logger = logging.getLogger(__name__)

SCALE_FACTOR = 1

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))

EYES_BROWS_POINTS = (
    LEFT_EYE_POINTS + RIGHT_EYE_POINTS + LEFT_BROW_POINTS + RIGHT_BROW_POINTS
)

NOSE_MOUTH_POINTS = NOSE_POINTS + MOUTH_POINTS

# Points used to line up the images.
ALIGN_POINTS = (
    LEFT_BROW_POINTS +
    RIGHT_EYE_POINTS +
    LEFT_EYE_POINTS +
    RIGHT_BROW_POINTS +
    NOSE_POINTS +
    MOUTH_POINTS
)

class TooManyFaces(Exception):
    pass

class NoFaces(Exception):
    pass


class Faceswap:
    def __init__(self,
        predictor_path,
        overlay_eyesbrows = True,
        overlay_nosemouth = True,
        feather = FEATHER_AMOUNT,
        blur = BLUR_AMOUNT,
        raise_exceptions = False
    ):
        self.predictor_path = predictor_path
        self.blur = blur
        self.detector = dlib.get_frontal_face_detector()
        self.feather = feather
        self.predictor = dlib.shape_predictor(self.predictor_path)
        self.overlay_points = []
        self.landmark_hashes = {}

        if overlay_eyesbrows:
            self.overlay_points.append(EYES_BROWS_POINTS)

        if overlay_nosemouth:
            self.overlay_points.append(NOSE_MOUTH_POINTS)

    def _get_landmarks(self, im):
        # This is by far the slowest part of the whole algorithm, so we
        # cache the landmarks if the image is the same, especially when
        # dealing with videos this makes things twice as fast
        img_hash = str(abs(hash(im.data.tobytes())))

        if config.CACHE_LANDMARKS and img_hash in self.landmark_hashes:
            logging.debug("Landmarks are cached, return those")
            return self.landmark_hashes[img_hash]

        profiler.tick("start_detector")
        rects = self.detector(im, 1)
        profiler.tick("end_detector")

        if len(rects) > 1:
            raise TooManyFaces
        if len(rects) == 0:
            raise NoFaces

        landmarks = numpy.matrix([[p.x, p.y] for p in self.predictor(im, rects[0]).parts()])

        # Save to image cache
        self.landmark_hashes[img_hash] = landmarks

        return landmarks

    def _annotate_landmarks(self, im, landmarks):
        im = im.copy()
        for idx, point in enumerate(landmarks):
            pos = (point[0, 0], point[0, 1])
            cv2.putText(im, str(idx), pos,
                        fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                        fontScale=0.4,
                        color=(0, 0, 255))
            cv2.circle(im, pos, 3, color=(0, 255, 255))
        return im

    def _draw_convex_hull(self, im, points, color):
        points = cv2.convexHull(points)
        cv2.fillConvexPoly(im, points, color=color)

    def _get_face_mask(self, im, landmarks):
        im = numpy.zeros(im.shape[:2], dtype=numpy.float64)

        for group in self.overlay_points:
            self._draw_convex_hull(im,
                             landmarks[group],
                             color=1)

        im = numpy.array([im, im, im]).transpose((1, 2, 0))

        im = (cv2.GaussianBlur(im, (self.feather, self.feather), 0) > 0) * 1.0
        im = cv2.GaussianBlur(im, (self.feather, self.feather), 0)

        return im

    def _transformation_from_points(self, points1, points2):
        """
        Return an affine transformation [s * R | T] such that:

            sum ||s*R*p1,i + T - p2,i||^2

        is minimized.

        """
        # Solve the procrustes problem by subtracting centroids, scaling by the
        # standard deviation, and then using the SVD to calculate the rotation. See
        # the following for more details:
        #   https://en.wikipedia.org/wiki/Orthogonal_Procrustes_problem

        points1 = points1.astype(numpy.float64)
        points2 = points2.astype(numpy.float64)

        c1 = numpy.mean(points1, axis=0)
        c2 = numpy.mean(points2, axis=0)
        points1 -= c1
        points2 -= c2

        s1 = numpy.std(points1)
        s2 = numpy.std(points2)
        points1 /= s1
        points2 /= s2

        U, S, Vt = numpy.linalg.svd(points1.T * points2)

        # The R we seek is in fact the transpose of the one given by U * Vt. This
        # is because the above formulation assumes the matrix goes on the right
        # (with row vectors) where as our solution requires the matrix to be on the
        # left (with column vectors).
        R = (U * Vt).T

        return numpy.vstack([numpy.hstack(((s2 / s1) * R,
                                           c2.T - (s2 / s1) * R * c1.T)),
                             numpy.matrix([0., 0., 1.])])

    def _read_im_and_landmarks(self, fname):
        logger.debug(f"Reading {fname} for landmarks")
        profiler.tick("start _read_im_and_landmarks (imread)")
        im = cv2.imread(fname, cv2.IMREAD_COLOR)
        profiler.tick("end _read_im_and_landmarks (imread)")

        im = cv2.resize(im, (im.shape[1] * SCALE_FACTOR,
                             im.shape[0] * SCALE_FACTOR))

        profiler.tick("_read_im_and_landmarks (resize)")

        s = self._get_landmarks(im)
        profiler.tick("_read_im_and_landmarks (_get_landmarks)")

        return im, s

    def _warp_im(self, im, M, dshape):
        output_im = numpy.zeros(dshape, dtype=im.dtype)
        cv2.warpAffine(im,
                       M[:2],
                       (dshape[1], dshape[0]),
                       dst=output_im,
                       borderMode=cv2.BORDER_TRANSPARENT,
                       flags=cv2.WARP_INVERSE_MAP)
        return output_im

    def _correct_colours(self, im1, im2, landmarks1):
        blur_amount = self.blur * numpy.linalg.norm(
                                  numpy.mean(landmarks1[LEFT_EYE_POINTS], axis=0) -
                                  numpy.mean(landmarks1[RIGHT_EYE_POINTS], axis=0))
        blur_amount = int(blur_amount)
        if blur_amount % 2 == 0:
            blur_amount += 1
        im1_blur = cv2.GaussianBlur(im1, (blur_amount, blur_amount), 0)
        im2_blur = cv2.GaussianBlur(im2, (blur_amount, blur_amount), 0)

        # Avoid divide-by-zero errors.
        im2_blur += (128 * (im2_blur <= 1.0)).astype(im2_blur.dtype)

        return (im2.astype(numpy.float64) * im1_blur.astype(numpy.float64) /
                                                    im2_blur.astype(numpy.float64))

    def faceswap(self, head, face, output):
        profiler.tick("start faceswap")
        logger.debug(f"Faceswap {head} on {face} as {output}")

        im1, landmarks1 = self._read_im_and_landmarks(head)
        profiler.tick("_read_im_and_landmarks (head)")
        im2, landmarks2 = self._read_im_and_landmarks(face)
        profiler.tick("_read_im_and_landmarks (face)")

        M = self._transformation_from_points(landmarks1[ALIGN_POINTS],
                                       landmarks2[ALIGN_POINTS])

        profiler.tick("_transformation_from_points")

        mask = self._get_face_mask(im2, landmarks2)
        profiler.tick("_get_face_mask")

        warped_mask = self._warp_im(mask, M, im1.shape)
        profiler.tick("_warp_im")

        combined_mask = numpy.max([self._get_face_mask(im1, landmarks1), warped_mask],
                                  axis=0)
        profiler.tick("combined_mask")

        warped_im2 = self._warp_im(im2, M, im1.shape)
        profiler.tick("_warp_im")

        warped_corrected_im2 = self._correct_colours(im1, warped_im2, landmarks1)
        profiler.tick("_correct_colours")

        output_im = im1 * (1.0 - combined_mask) + warped_corrected_im2 * combined_mask
        profiler.tick("output_im")

        cv2.imwrite(output, output_im)
        profiler.tick("imwrite")

        if config.PROFILE:
            profiler.dump_events()
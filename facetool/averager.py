# Based on the Face Averager by Satya Mallick
# < https://github.com/spmallick/learnopencv/blob/master/FaceAverage/faceAverage.py >

import cv2
import logging
import numpy as np
import pdb
from .constants import DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT
from .faceaverage import similarityTransform, rectContains, calculateDelaunayTriangles
from .faceaverage import constrainPoint, applyAffineTransform, warpTriangle
from .landmarks import Landmarks
from .path import Path

logger = logging.getLogger(__name__)

class Averager:
    def __init__(self,
        predictor_path,
        img_width = DEFAULT_IMAGE_WIDTH,
        img_height = DEFAULT_IMAGE_HEIGHT
    ):
        self.predictor_path = predictor_path
        self.landmarks = Landmarks(self.predictor_path)
        self.img_width = img_width
        self.img_height = img_height

    def _read_image(self, path):
        logging.debug(f"Reading image {path}")

        img = cv2.imread(str(path))
        img = np.float32(img) / 255.0
        return img

    def average(self, input_dir, output_file):
        logging.debug(f"Reading images in {input_dir} to {output_file}")

        if not Path(input_dir).is_dir():
            raise Exception("Input for averaging faces should be a directory")

        images = []
        allPoints = []

        for imgpath in Path(input_dir).images():
            images.append(self._read_image(imgpath))

            # Convert from dlib points to regular points
            imgPoints = self.landmarks.get_landmarks(imgpath)
            allPoints.append([[p.x, p.y] for p in imgPoints])

        # For easy reference
        w = self.img_width
        h = self.img_height

        # Eye corners
        eyecornerDst = [
            (np.int(0.3 * w ), np.int(h / 3)), (np.int(0.7 * w ), np.int(h / 3))
        ]

        imagesNorm = []
        pointsNorm = []

        # Add boundary points for delaunay triangulation
        boundaryPts = np.array([
            (0,0), (w/2,0), (w-1,0), (w-1,h/2),
            ( w-1, h-1 ), ( w/2, h-1 ), (0, h-1), (0,h/2)
        ])

        # Initialize location of average points to 0s
        pointsAvg = np.array(
            [(0,0)]* ( len(allPoints[0]) + len(boundaryPts) ), np.float32()
        )

        n = len(allPoints[0])

        numImages = len(images)

        # Warp images and trasnform landmarks to output coordinate system,
        # and find average of transformed landmarks.

        for i in range(0, numImages):

            points1 = allPoints[i]

            # Corners of the eye in input image
            eyecornerSrc  = [ allPoints[i][36], allPoints[i][45] ]

            # Compute similarity transform
            tform = similarityTransform(eyecornerSrc, eyecornerDst)

            # Apply similarity transformation
            img = cv2.warpAffine(images[i], tform, (w,h))

            # Apply similarity transform on points
            points2 = np.reshape(np.array(points1), (68,1,2))

            points = cv2.transform(points2, tform)

            points = np.float32(np.reshape(points, (68, 2)))

            # Append boundary points. Will be used in Delaunay Triangulation
            points = np.append(points, boundaryPts, axis=0)

            # Calculate location of average landmark points.
            pointsAvg = pointsAvg + points / numImages

            pointsNorm.append(points)
            imagesNorm.append(img)



        # Delaunay triangulation
        rect = (0, 0, w, h)
        dt = calculateDelaunayTriangles(rect, np.array(pointsAvg))

        # Output image
        output = np.zeros((h,w,3), np.float32())

        # Warp input images to average image landmarks
        for i in range(0, len(imagesNorm)) :
            img = np.zeros((h,w,3), np.float32())
            # Transform triangles one by one
            for j in range(0, len(dt)) :
                tin = []
                tout = []

                for k in range(0, 3) :
                    pIn = pointsNorm[i][dt[j][k]]
                    pIn = constrainPoint(pIn, w, h)

                    pOut = pointsAvg[dt[j][k]]
                    pOut = constrainPoint(pOut, w, h)

                    tin.append(pIn)
                    tout.append(pOut)


                warpTriangle(imagesNorm[i], img, tin, tout)


            # Add image intensities for averaging
            output = output + img


        # Divide by numImages to get average
        output = output / numImages

        # Display result
        cv2.imshow('image', output)
        cv2.waitKey(0)

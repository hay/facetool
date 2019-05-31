# Code adapted from < https://github.com/wuhuikai/FaceSwap >
from .constants import FEATHER_AMOUNT, BLUR_AMOUNT
from .util import TooManyFacesError, NoFacesError

import logging
import cv2
import dlib
import numpy as np
import scipy.spatial as spatial
import logging

logger = logging.getLogger(__name__)

class Faceswap3d:
    def __init__(self,
        predictor_path,
        overlay_eyesbrows = True,
        overlay_nosemouth = True,
        feather = FEATHER_AMOUNT,
        blur = BLUR_AMOUNT,
        warp_3d = False,
        correct_color = True
    ):
        self.predictor_path = predictor_path
        self.correct_color = correct_color
        self.warp_3d = warp_3d
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(self.predictor_path)

    ## 3D Transform
    def _bilinear_interpolate(self, img, coords):
        """ Interpolates over every image channel
        http://en.wikipedia.org/wiki/Bilinear_interpolation
        :param img: max 3 channel image
        :param coords: 2 x _m_ array. 1st row = xcoords, 2nd row = ycoords
        :returns: array of interpolated pixels with same shape as coords
        """
        int_coords = np.int32(coords)
        x0, y0 = int_coords
        dx, dy = coords - int_coords

        # 4 Neighour pixels
        q11 = img[y0, x0]
        q21 = img[y0, x0 + 1]
        q12 = img[y0 + 1, x0]
        q22 = img[y0 + 1, x0 + 1]

        btm = q21.T * dx + q11.T * (1 - dx)
        top = q22.T * dx + q12.T * (1 - dx)
        inter_pixel = top * dy + btm * (1 - dy)

        return inter_pixel.T

    def _grid_coordinates(self, points):
        """ x,y grid coordinates within the ROI of supplied points
        :param points: points to generate grid coordinates
        :returns: array of (x, y) coordinates
        """
        xmin = np.min(points[:, 0])
        xmax = np.max(points[:, 0]) + 1
        ymin = np.min(points[:, 1])
        ymax = np.max(points[:, 1]) + 1

        return np.asarray([(x, y) for y in range(ymin, ymax)
                           for x in range(xmin, xmax)], np.uint32)


    def _process_warp(self, src_img, result_img, tri_affines, dst_points, delaunay):
        """
        Warp each triangle from the src_image only within the
        ROI of the destination image (points in dst_points).
        """
        roi_coords = self._grid_coordinates(dst_points)

        # indices to vertices. -1 if pixel is not in any triangle
        roi_tri_indices = delaunay.find_simplex(roi_coords)

        for simplex_index in range(len(delaunay.simplices)):
            coords = roi_coords[roi_tri_indices == simplex_index]
            num_coords = len(coords)
            out_coords = np.dot(tri_affines[simplex_index],
                                np.vstack((coords.T, np.ones(num_coords))))
            x, y = coords.T
            result_img[y, x] = self._bilinear_interpolate(src_img, out_coords)

        return None


    def _triangular_affine_matrices(self, vertices, src_points, dst_points):
        """
        Calculate the affine transformation matrix for each
        triangle (x,y) vertex from dst_points to src_points
        :param vertices: array of triplet indices to corners of triangle
        :param src_points: array of [x, y] points to landmarks for source image
        :param dst_points: array of [x, y] points to landmarks for destination image
        :returns: 2 x 3 affine matrix transformation for a triangle
        """
        ones = [1, 1, 1]
        for tri_indices in vertices:
            src_tri = np.vstack((src_points[tri_indices, :].T, ones))
            dst_tri = np.vstack((dst_points[tri_indices, :].T, ones))
            mat = np.dot(src_tri, np.linalg.inv(dst_tri))[:2, :]
            yield mat


    def _warp_image_3d(self, src_img, src_points, dst_points, dst_shape, dtype=np.uint8):
        rows, cols = dst_shape[:2]
        result_img = np.zeros((rows, cols, 3), dtype=dtype)

        delaunay = spatial.Delaunay(dst_points)
        tri_affines = np.asarray(list(self._triangular_affine_matrices(
            delaunay.simplices, src_points, dst_points)))

        self._process_warp(src_img, result_img, tri_affines, dst_points, delaunay)

        return result_img

    ## 2D Transform
    def _transformation_from_points(self, points1, points2):
        points1 = points1.astype(np.float64)
        points2 = points2.astype(np.float64)

        c1 = np.mean(points1, axis=0)
        c2 = np.mean(points2, axis=0)
        points1 -= c1
        points2 -= c2

        s1 = np.std(points1)
        s2 = np.std(points2)
        points1 /= s1
        points2 /= s2

        U, S, Vt = np.linalg.svd(np.dot(points1.T, points2))
        R = (np.dot(U, Vt)).T

        return np.vstack([np.hstack([s2 / s1 * R,
                                    (c2.T - np.dot(s2 / s1 * R, c1.T))[:, np.newaxis]]),
                          np.array([[0., 0., 1.]])])


    def _warp_image_2d(self, im, M, dshape):
        output_im = np.zeros(dshape, dtype=im.dtype)
        cv2.warpAffine(im,
                       M[:2],
                       (dshape[1], dshape[0]),
                       dst=output_im,
                       borderMode=cv2.BORDER_TRANSPARENT,
                       flags=cv2.WARP_INVERSE_MAP)

        return output_im


    ## Generate Mask
    def _mask_from_points(self, size, points,erode_flag=1):
        radius = 10  # kernel size
        kernel = np.ones((radius, radius), np.uint8)

        mask = np.zeros(size, np.uint8)
        cv2.fillConvexPoly(mask, cv2.convexHull(points), 255)
        if erode_flag:
            mask = cv2.erode(mask, kernel,iterations=1)

        return mask


    ## Color Correction
    def _correct_colours(self, im1, im2, landmarks1):
        COLOUR_CORRECT_BLUR_FRAC = 0.75
        LEFT_EYE_POINTS = list(range(42, 48))
        RIGHT_EYE_POINTS = list(range(36, 42))

        blur_amount = COLOUR_CORRECT_BLUR_FRAC * np.linalg.norm(
                                  np.mean(landmarks1[LEFT_EYE_POINTS], axis=0) -
                                  np.mean(landmarks1[RIGHT_EYE_POINTS], axis=0))
        blur_amount = int(blur_amount)
        if blur_amount % 2 == 0:
            blur_amount += 1
        im1_blur = cv2.GaussianBlur(im1, (blur_amount, blur_amount), 0)
        im2_blur = cv2.GaussianBlur(im2, (blur_amount, blur_amount), 0)

        # Avoid divide-by-zero errors.
        im2_blur = im2_blur.astype(int)
        im2_blur += 128*(im2_blur <= 1)

        result = im2.astype(np.float64) * im1_blur.astype(np.float64) / im2_blur.astype(np.float64)
        result = np.clip(result, 0, 255).astype(np.uint8)

        return result


    ## Copy-and-paste
    def _apply_mask(self, img, mask):
        """ Apply mask to supplied image
        :param img: max 3 channel image
        :param mask: [0-255] values in mask
        :returns: new image with mask applied
        """
        masked_img = cv2.bitwise_and(img,img,mask=mask)

        return masked_img

    ## Alpha blending
    def _alpha_feathering(self, src_img, dest_img, img_mask, blur_radius=15):
        mask = cv2.blur(img_mask, (blur_radius, blur_radius))
        mask = mask / 255.0

        result_img = np.empty(src_img.shape, np.uint8)
        for i in range(3):
            result_img[..., i] = src_img[..., i] * mask + dest_img[..., i] * (1-mask)

        return result_img


    def _select_face(self, im, r = 10):
        faces = self.detector(im)

        if len(faces) > 1:
            raise TooManyFacesError
        elif len(faces) == 0:
            raise NoFacesError
        else:
            bbox = faces[0]

        # Get the landmarks/parts for the face in box d.
        shape = self.predictor(im, bbox)

        # loop over the 68 facial landmarks and convert them
        # to a 2-tuple of (x, y)-coordinates
        points = np.asarray(list([p.x, p.y] for p in shape.parts()), dtype=np.int)

        # points = np.asarray(self.face_points_detection(im, bbox))

        im_w, im_h = im.shape[:2]
        left, top = np.min(points, 0)
        right, bottom = np.max(points, 0)

        x, y = max(0, left-r), max(0, top-r)
        w, h = min(right+r, im_h)-x, min(bottom+r, im_w)-y

        return points - np.asarray([[x, y]]), (x, y, w, h), im[y:y+h, x:x+w]


    def faceswap(self, head, face, output):
        logger.debug(f"Faceswap {head} on {face} as {output}")

        src_img = cv2.imread(face)
        dst_img = cv2.imread(head)

        # Select src face
        src_points, src_shape, src_face = self._select_face(src_img)

        # Select dst face
        dst_points, dst_shape, dst_face = self._select_face(dst_img)

        h, w = dst_face.shape[:2]

        ### Warp Image
        if self.warp_3d:
            logging.debug(f"Warping in 3d")
            ## 3d warp
            warped_src_face = self._warp_image_3d(src_face, src_points[:48], dst_points[:48], (h, w))
        else:
            logging.debug(f"Warping in 2d")
            ## 2d warp
            src_mask = self._mask_from_points(src_face.shape[:2], src_points)
            src_face = self._apply_mask(src_face, src_mask)

            # Correct Color for 2d warp
            if self.correct_color:
                warped_dst_img = self._warp_image_3d(dst_face, dst_points[:48], src_points[:48], src_face.shape[:2])
                src_face = self._correct_colours(warped_dst_img, src_face, src_points)

            # Warp
            warped_src_face = self._warp_image_2d(
                src_face,
                self._transformation_from_points(dst_points, src_points),
                (h, w, 3)
            )

        ## Mask for blending
        mask = self._mask_from_points((h, w), dst_points)
        mask_src = np.mean(warped_src_face, axis=2) > 0
        mask = np.asarray(mask*mask_src, dtype=np.uint8)

        ## Correct color
        if self.warp_3d and self.correct_color:
            warped_src_face = self._apply_mask(warped_src_face, mask)
            dst_face_masked = self._apply_mask(dst_face, mask)
            warped_src_face = self._correct_colours(dst_face_masked, warped_src_face, dst_points)

        ## Shrink the mask
        kernel = np.ones((10, 10), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)

        ## Poisson Blending
        r = cv2.boundingRect(mask)
        center = ((r[0] + int(r[2] / 2), r[1] + int(r[3] / 2)))
        output_data = cv2.seamlessClone(warped_src_face, dst_face, mask, center, cv2.NORMAL_CLONE)

        x, y, w, h = dst_shape
        dst_img_cp = dst_img.copy()
        dst_img_cp[y:y+h, x:x+w] = output_data
        output_data = dst_img_cp

        cv2.imwrite(output, output_data)
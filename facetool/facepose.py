# Based on < http://www.learnopencv.com/head-pose-estimation-using-opencv-and-dlib/ >
# And < https://www.learnopencv.com/rotation-matrix-to-euler-angles/ >
import numpy as np
import cv2
from math import asin, acos, cos, pi

POINTS_3D =  [
    (0.0, 0.0, 0.0),             # Nose tip
    (0.0, -330.0, -65.0),        # Chin
    (-225.0, 170.0, -135.0),     # Left eye left corner
    (225.0, 170.0, -135.0),      # Right eye right corne
    (-150.0, -150.0, -125.0),    # Left Mouth corner
    (150.0, -150.0, -125.0)      # Right mouth corner
]

# From < https://stackoverflow.com/questions/14515200/python-opencv-solvepnp-yields-wrong-translation-vector >
def rot_matrix_to_euler(R):
    y_rot = asin(R[2][0])
    x_rot = acos(R[2][2]/cos(y_rot))
    z_rot = acos(R[0][0]/cos(y_rot))
    y_rot_angle = y_rot *(180/pi)
    x_rot_angle = x_rot *(180/pi)
    z_rot_angle = z_rot *(180/pi)
    return x_rot_angle,y_rot_angle,z_rot_angle

def detect_pose(img, shape, draw_direction_line = False, draw_points = False):
    height, width, channels = img.shape

    pose_points = {
        "nose_tip" : shape[30],
        "chin" : shape[8],
        "left_eye_left_corner" : shape[36],
        "right_eye_right_corner" : shape[45],
        "left_mouth_corner" : shape[48],
        "right_mouth_corner" : shape[54]
    }

    # Convert point to tuple
    pose_points = {k:(p.x, p.y) for k, p in pose_points.items()}

    image_points = np.array(list(pose_points.values()), dtype = "double")
    model_points = np.array(POINTS_3D)

    # Camera internals
    focal_length = width
    center = (width / 2, height / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype = "double")

    dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion

    (success, rotation_vector, translation_vector) = cv2.solvePnP(
        model_points,
        image_points,
        camera_matrix,
        dist_coeffs
    )

    if draw_direction_line:
        (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)
        p1 = ( int(image_points[0][0]), int(image_points[0][1]))
        p2 = ( int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
        cv2.line(img, p1, p2, (255,0,0), 5)

    if draw_points:
        for p in pose_points.values():
            cv2.circle(img, p, 5, (255, 0, 0), -1)

    np_rodrigues = np.asarray(rotation_vector[:,:],np.float64)
    rot_matrix = cv2.Rodrigues(np_rodrigues)[0]

    if success:
        return rot_matrix_to_euler(rot_matrix)
    else:
        return False
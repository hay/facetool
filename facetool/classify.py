import logging
logger = logging.getLogger(__name__)

from .profiler import Profiler
from . import config, resnet
profiler = Profiler("classify.py")

import os
import cv2
import dlib
import numpy as np
import tensorflow as tf
from imutils.face_utils import FaceAligner
from imutils.face_utils import rect_to_bb

profiler.tick("Libraries imported")

def get_gender(gender):
    if gender == 0:
        return "female"
    elif gender == 1:
        return "male"
    else:
        return "unknown"

class Classify:
    def __init__(self, model_path, predictor_path, use_cuda = False):
        self.model_path = model_path
        self.predictor_path = predictor_path
        self.use_cuda = use_cuda

        if not use_cuda:
            os.environ['CUDA_VISIBLE_DEVICES'] = ''

        self._create_session()

    def classify(self, path):
        aligned_image, image, rect_nums, XY = self._load_image(path)
        profiler.tick("Loaded image")
        ages, genders = self._evaluate(aligned_image)
        profiler.tick("Evaluated image")

        if config.PROFILE:
            profiler.dump_events()

        return {
            "ages" : ages.tolist(),
            "genders" : [get_gender(g) for g in genders.tolist()]
        }

    def _create_session(self):
        logger.debug("Creating session")

        with tf.Graph().as_default():
            self.session = tf.Session()
            images_pl = tf.placeholder(tf.float32, shape=[None, 160, 160, 3], name='input_image')
            images = tf.map_fn(lambda frame: tf.reverse_v2(frame, [-1]), images_pl) #BGR TO RGB
            images_norm = tf.map_fn(lambda frame: tf.image.per_image_standardization(frame), images)
            train_mode = tf.placeholder(tf.bool)
            age_logits, gender_logits, _ = resnet.inference(images_norm, keep_probability=0.8,
                                                                         phase_train=train_mode,
                                                                         weight_decay=1e-5)
            gender = tf.argmax(tf.nn.softmax(gender_logits), 1)
            age_ = tf.cast(tf.constant([i for i in range(0, 101)]), tf.float32)
            age = tf.reduce_sum(tf.multiply(tf.nn.softmax(age_logits), age_), axis=1)

            init_op = tf.group(
                tf.global_variables_initializer(),
                tf.local_variables_initializer()
            )

            self.session.run(init_op)
            saver = tf.train.Saver()
            ckpt = tf.train.get_checkpoint_state(self.model_path)

            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(self.session, ckpt.model_checkpoint_path)
                self._age = age
                self._gender = gender
                self._images_pl = images_pl
                self._train_mode = train_mode
                logger.debug("Session restorted")
            else:
                logger.debug("Could not create session")

            profiler.tick("Created session")

    def _evaluate(self, aligned_images):
        return self.session.run(
            [self._age, self._gender],

            feed_dict = {
                self._images_pl: aligned_images,
                self._train_mode: False
            }
        )

    def _load_image(self, image_path):
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(self.predictor_path)
        fa = FaceAligner(predictor, desiredFaceWidth=160)
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 2)
        rect_nums = len(rects)
        XY, aligned_images = [], []

        if rect_nums == 0:
            aligned_images.append(image)

            return aligned_images, image, rect_nums, XY
        else:
            for i in range(rect_nums):
                aligned_image = fa.align(image, gray, rects[i])
                aligned_images.append(aligned_image)
                (x, y, w, h) = rect_to_bb(rects[i])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), color=(255, 0, 0), thickness=2)
                XY.append((x, y))

            return np.array(aligned_images), image, rect_nums, XY
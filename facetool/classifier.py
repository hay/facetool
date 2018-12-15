from .classify import Classify
import logging
logger = logging.getLogger(__name__)

class Classifier:
    def __init__(self, data_directory, predictor_path):
        self.data_directory = data_directory
        self.predictor_path = predictor_path
        self._classify = Classify(
            model_path = data_directory,
            predictor_path = predictor_path
        )

    def classify(self, path):
        logging.debug(f"Classifying <{path}>")
        data = self._classify.classify(path)
        print(data)
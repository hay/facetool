from .classify import Classify
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class Classifier:
    def __init__(self, data_directory, predictor_path, output_format):
        self.data_directory = data_directory
        self.output_format = output_format
        self.predictor_path = predictor_path
        self._classify = Classify(
            model_path = data_directory,
            predictor_path = predictor_path
        )

        if self.output_format == "csv":
            self.output = []

    def classify(self, path):
        logging.debug(f"Classifying <{path}>")
        data = self._classify.classify(path)

        if self.output_format == "csv":
            # Only one value for ages/genders for now
            self.output.append({
                "path" : path,
                "gender" : data["genders"][0],
                "age" : data["ages"][0]
            })
        else:
            print(data)

    def to_csv(self, path):
        logging.debug("Saving csv")
        df = pd.DataFrame(self.output)
        df.to_csv(path)
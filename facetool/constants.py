from pathlib import Path as OrigPath
path = OrigPath(__file__)

BLUR_AMOUNT = 0.6
DATA_DIRECTORY = path.parent.parent.joinpath("data")
DEFAULT_FRAMERATE = 30
DEFAULT_IMAGE_WIDTH = 600
DEFAULT_IMAGE_HEIGHT = 600
DEFAULT_TRESHOLD = 0.6
FEATHER_AMOUNT = 11
IMAGE_EXTENSIONS = (".jpg", ".png")
PREDICTOR_PATH = f"{DATA_DIRECTORY}/landmarks.dat"
class ArgumentError(Exception):
    pass

class FaceError(Exception):
    pass

class TooManyFacesError(FaceError):
    pass

class NoFacesError(FaceError):
    pass
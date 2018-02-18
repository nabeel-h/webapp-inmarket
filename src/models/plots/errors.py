__author__ = "nblhn"

class PlotError(Exception):
    def __init__(self, message):
        self.message = message

class PlotFailed(PlotError):
    pass

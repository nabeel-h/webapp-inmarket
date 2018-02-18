__author__ = "nblhn"

class SheetErrors(Exception):
    def __init__(self, message):
        self.message = message

class NamedRangeError(SheetErrors):
    pass
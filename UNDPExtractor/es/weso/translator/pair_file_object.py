__author__ = 'Dani'


class PairFileObject(object):
    """
    It represents an association between a file and another object. The file will be represented by its path.
    We don't expect an instance of a concrete type of the other object. No operation will be applied over it, an
    instance of a PairFileObject has been thought to store everything in its "other_object field.
    """
    def __init__(self, file_path, other_object):
        self.file_path = file_path
        self.other_object = other_object


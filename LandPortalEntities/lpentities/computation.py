"""
Created on 02/02/2014

@author: Miguel Otero
"""


class Computation(object):
    """
    classdocs
    """
    RAW = "Raw"
    ESTIMATED = "Raw"  # At this point, we are not going to make a difference between raw and estimated.
                        # We would need to expand the ontology to do that
    CALCULATED = "Computed"

    _desc_dict = {RAW: "Raw data values that have been collected from a datasource without any normalisation process.",
                  ESTIMATED: "Raw data values that have been collected from a datasource without any normalisation process.",
                  CALCULATED: "Data values that have been computed by some algorithm."}



    def __init__(self, uri=None):
        """
        Constructor
        """
        self._uri = uri

    @staticmethod
    def get_desc_of_uri(target_uri):
        return Computation._desc_dict[target_uri]
        
    def __get_uri(self):
        return self._uri
    
    def __set_uri(self, uri):
        if uri == self.RAW or uri == self.ESTIMATED or uri == self.CALCULATED:
            self._uri = uri
        else:
            raise ValueError("Provided uri not in the given values")
        
    uri = property(fget=__get_uri, fset=__set_uri, doc="Kind of uri computation")
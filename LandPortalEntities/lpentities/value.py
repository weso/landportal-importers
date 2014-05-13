"""
Created on 02/02/2014

@author: Miguel Otero
"""


class Value(object):
    """
    classdocs
    """

    MISSING = "obsStatus-M"
    AVAILABLE = "obsStatus-A"
    FLOAT = "float"
    INTEGER = "int"


    def __init__(self, value=None, value_type=None, obs_status=None):
        """
        Constructor
        """
        self.value = value
        self._value_type = value_type
        self._obs_status = obs_status
        
    def __get_value_type(self):
        return self._value_type
    
    def __set_value_type(self, value_type):
        if value_type == self.INTEGER or value_type == self.FLOAT :
            self._value_type = value_type
        else:
            raise ValueError("Value type not in the given ones")
        
    value_type = property(fget=__get_value_type,
                      fset=__set_value_type,
                      doc="The value type of the value")
    
    def __get_obs_status(self):
        return self._obs_status
    
    def __set_obs_status(self, obs_status):
        if obs_status == self.MISSING or obs_status == self.AVAILABLE:
            self._obs_status = obs_status
        else:
            raise ValueError("Observation status not in the given ones")
        
    obs_status = property(fget=__get_obs_status,
                      fset=__set_obs_status,
                      doc="The Status of the value")
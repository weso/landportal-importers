'''
Created on 02/02/2014

@author: Miguel Otero
'''

class MeasurementUnit(object):
    '''
    classdocs
    '''

    RANK = "rank"
    INDEX = "index"
    UNITS = "units"
    SQ_KM = "sq. km"
    PERCENTAGE = "%"


    #Enum possible convert_to values


    def __init__(self, name=None, convert_to=None, factor=1):
        '''
        Constructor
        '''
        self.name = name
        self._convert_to = convert_to
        self._factor = factor

    def __get_convert_to(self):
        return self._convert_to

    def __set_convert_to(self, value):
        if value not in [self.RANK, self.INDEX, self.UNITS, self.SQ_KM, self.PERCENTAGE]:
            raise ValueError("Invalid provided convert_to value: {0}".format(value))
        self._convert_to = value

    convert_to = property(fget=__get_convert_to,
                          fset=__set_convert_to,
                          doc="The MeasurementUnit is convertible to this value")

    def __get_factor(self):
        return self._factor
    
    def __set_factor(self, factor):
        if factor >= 0:
            self._factor = factor
        else:
            raise ValueError("Conversion factor must be at least zero")
        
    factor = property(fget=__get_factor,
                      fset=__set_factor,
                      doc="The MeasurementUnit is adjusted by this factor")
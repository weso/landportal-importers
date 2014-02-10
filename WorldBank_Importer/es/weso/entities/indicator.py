'''
Created on 19/12/2013

@author: Nacho
'''

class Indicator(object):
    '''
    classdocs
    '''


    def __init__(self, name = None, description = None,
                 license_type = None, measurement_unit = None):
        '''
        Constructor
        '''
        self.name = name
        self.id = "http://landportal.info/ontology/indicator/" + name
        self.description = description
        self.license_type = license_type
        self.measurement_unit = measurement_unit
        
'''
Created on 02/02/2014

@author: Miguel Otero
'''

class License(object):
    '''
    classdocs
    '''


    def __init__(self, name = None, description = None, republish = None, url = None):
        '''
        Constructor
        '''
        self.name = name
        self.description = description
        self.republish = republish
        self.url = url
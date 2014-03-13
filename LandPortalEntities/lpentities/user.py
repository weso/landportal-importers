'''
Created on 02/02/2014

@author: Miguel Otero
'''

class User(object):
    '''
    classdocs
    '''


    def __init__(self, user_id=None, ip=None, timestamp=None, organization=None):
        '''
        Constructor
        '''
        self.user_id = user_id
        self.ip = ip
        self.timestamp = timestamp
        self.organization = organization
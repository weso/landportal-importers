'''
Created on 02/02/2014

@author: Miguel Otero
'''

class Organization(object):
    '''
    classdocs
    '''


    def __init__(self, name = None, url = None, is_part_of = None):
        '''
        Constructor
        '''
        self.name = name
        self.url = url
        self.is_part_of = is_part_of
        self.data_sources = []
        self.users = []


    def add_user(self, user):
        self.users.append(user)
        user.organization = self

    def add_data_source(self, data_source):
        self.data_sources.append(data_source)
        data_source.organization = self
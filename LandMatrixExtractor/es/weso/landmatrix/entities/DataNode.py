'''
Created on 22/01/2014

@author: Dani
'''

class DataNode(object):
    '''
    classdocs
    '''


    def __init__(self, country, info_groups):
        self.country = country
        self.info_groups = info_groups
        '''
        Constructor
        '''
    
    def add_info_group(self, info_group):
            self.info_groups.append(info_group)
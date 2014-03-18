'''
Created on 13/01/2014

@author: Dani

This class consist in a data structure formed by the name of 
a data table and it URL to dowload it data from the net.
The URL does not work directly, a "." and a valid extension 
(xml, csv, json) should be appended at the end of the URL.
'''

class DataTable(object):
    '''
    classdocs
    '''


    def __init__(self, name, url):
        '''
        Constructor
        '''
        self.name = name
        self.url = url
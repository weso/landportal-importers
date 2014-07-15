'''
Created on 13/01/2014

@author: Dani
'''

class FileWriter(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def write_text_to_file(text, file_name):
        fileStream = open(str(file_name), "w")
        fileStream.write(text)
        fileStream.close()
    
    @staticmethod
    def write_binary_to_file(text, file_name):
        fileStream = open(str(file_name), "wb")
        fileStream.write(text)
        fileStream.close()
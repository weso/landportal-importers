'''
Created on May 15, 2014

@author: Borja
'''
import os
import urllib2

from data import __data__


class FileDownloader(object):
    
    def download_file(self, url, file_name):
        downloaded = False
        connection_attempts = 3
        
        #Check if folder exists
        if not os.path.exists(__data__.path()):
            os.makedirs(__data__.path())
        
        outpath = os.path.join(__data__.path(), os.path.basename(file_name))
        
        while not downloaded and connection_attempts > 0:
            try:
                downloaded_file = urllib2.urlopen(url)
                data = downloaded_file.read()
                with open(outpath, "wb") as code:
                    code.write(data)
                    
                downloaded = True
            except:
                downloaded = False
                connection_attempts -= 1
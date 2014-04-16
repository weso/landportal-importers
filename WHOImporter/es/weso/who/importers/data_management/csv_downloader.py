'''
Created on Apr 15, 2014

@author: Borja
'''

from os.path import os
import urllib2

from data import __data__


class CsvDownloader(object):

    def __init__(self, url_pattern, indicator_pattern, profile_pattern, countries_pattern, region_pattern):
        self._url_pattern = url_pattern
        self._indicator_pattern = indicator_pattern
        self._profile_pattern = profile_pattern
        self._countries_pattern = countries_pattern
        self._region_pattern = region_pattern

    def download_csv(self, indicator, profile, countries, regions, file_name):
        downloaded = False
        
        if os.path.exists(os.path.join(__data__.path(), os.path.basename(file_name))) :
            print "File already downloaded, please erase it"
        else :    
            connection_attempts = 3
            
            url = self._prepare_url(indicator, profile, countries, regions)
            
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
                    connection_attempts = connection_attempts-1
        
        return downloaded

    def _prepare_url(self, indicator, profile, countries, regions):
        result = self._url_pattern.replace(self._indicator_pattern, str(indicator))
        result = result.replace(self._profile_pattern, str(profile))
        result = result.replace(self._countries_pattern, str(countries))
        result = result.replace(self._region_pattern, str(regions))
        
        return result
        
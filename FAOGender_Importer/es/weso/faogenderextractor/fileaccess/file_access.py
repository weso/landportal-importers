'''
Created on 21/01/2014

@author: Miguel Otero
'''

import logging
from selenium import webdriver

class FileAccess(object):
    '''
    classdocs
    ''' 
    logger = logging.getLogger('file_access')

    def __init__(self):
        '''
        Constructor
        '''
    
    def obtain_countries(self):
        driver = webdriver.Firefox()
        driver.get('http://www.fao.org/gender/landrights/topic-selection/en/')
        radioButton = driver.find_element_by_id('7')
        radioButton.click()
        countryCheckboxes = driver.find_elements_by_css_selector("input[type='checkbox']")
        for checkbox in countryCheckboxes:
            checkbox.click()
        submitButton = driver.find_element_by_id('report')
        submitButton.click()
        countryReports = driver.find_elements_by_css_selector("div[id^='report_']")
        for countryReport in countryReports:
            country = countryReport.find_element_by_css_selector("div[class=country]")
            print country.text
        # Have to persist countryReports
        driver.close()
    
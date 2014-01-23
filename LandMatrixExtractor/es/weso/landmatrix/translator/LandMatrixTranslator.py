'''
Created on 22/01/2014

@author: Dani
'''

#from ConfigParser import ConfigParser
import logging
import xml.dom.minidom
from ConfigParser import ConfigParser
from es.weso.landmatrix.entities.DataNode import DataNode

class LandMatrixTranslator(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.log = logging.getLogger("land_matrix_extractor")
        self.config = ConfigParser()
        self.config.read("../../../../files/configuration.ini")
        
        self.root = xml.dom.minidom.parse(self.config.get("LAND_MATRIX", "target_file"))
        self.root = self.root.firstChild
        self.countries = {}     
        
    '''
    Translates the downloaded data into model objects. look_for_historical is a boolean
    that indicates if we have to consider old information or only bear in mind actual one
    '''
    def run(self, look_for_historical):
#         for item in self.root.childNodes:
#             if(item.nodeType == item.ELEMENT_NODE):
#                 print len(item.childNodes)
#                 self.treat_item_info(item, look_for_historical)
        for item in self.root.getElementsByTagName("item"):
            print len(item.childNodes)
            self.treat_item_info(item, look_for_historical)

        for key in self.countries.keys():
            c = self.countries.get(key)
            print c.country #+ " con " + len(c.info_groups)
    
    '''
    Adds a new country to the "countries" list with the item's data 
    or uploads an existing one with them 
    '''
    def treat_item_info(self, item, look_for_historical):    
        info = []
        data_node = None
        for field in item.getElementsByTagName("field"):
            if field.attributes.item(0).value == 'target_country':
                country_name = ""
                for child in field.childNodes:
                    if child.nodeType == child.TEXT_NODE:
                        country_name += str(child.data)
                data_node = self.get_target_country(country_name.strip())
            else:
                info.append(field)
        data_node.add_info_group(info)
                
                 
    
    def get_target_country(self, country_name):
        if self.countries.has_key(country_name):
            return self.countries.get(country_name)
        else:
            new_node = DataNode(country_name, [])
            self.countries[country_name] = new_node
            return new_node
        
    
    
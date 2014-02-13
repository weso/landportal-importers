'''
Created on 03/02/2014

@author: Dani
'''

from elementtree.ElementTree import Element, ElementTree

class ModelToXMLTransformer(object):
    '''
    Const containing names of tag or attributtes
    to use in the XML file
    '''
    ROOT ="dataset"
    INDICATORS = "indicators"
    INDICATOR = "indicator"
    SLICE = "slice"
    SLICE_ATT_ID = "id"
    
    OBSERVATION = "observation"
    OBSERVATION_ATT_ID = "id"
    OBSERVATION_ATT_COUNTRY = "country"
    OBSERVATION_ATT_VALUE = "value"
    OBSERVATION_ATT_MEASURE = "measure"
    OBSERVATION_ATT_INDICATOR = "indicator"
    OBSERVATION_ATT_TIME = "time"
    OBSERVATION_ATT_RELATED = "relatedObs"
    OBSERVATION_ATT_RELATION_PROPERTY = "relationProperty"
    
    OBSERVATION_ATT_COUNTRY_PREFIX = "http://landportal.info/ontology/country/"
    OBSERVATION_ATT_MEASURE_PREFIX = "http://landportal.info/ontology/country/currency/"
    OBSERVATION_ATT_INDICATOR_PREFIX = "http://landportal.info/ontology/country/indicator/"
    OBSERVATION_ATT_TIME_PREFIX = "http://landportal.info/ontology/year/"
    OBSERVATION_ATT_RELATION_PROPERTY_PREFIX = "http://landportal.info/ontology/relation/"
    #OBSERVATION_ATT_ID_PREFIX = NO PREFIX NEEDED
    #OBSERVATION_ATT_VALUE_PREFIX = "NO PREFIX NEEDED
    #OBSERVATION_ATT_RELATED_PREFIX = NO PREFIX NEEDED
    
    
    IMPORT_PROCESS = "importProcess"
    IMPORT_PROCESS_ATT_DATASOURCE = "datasource"
    IMPORT_PROCESS_ATT_TYPE = "type"
    IMPORT_PROCESS_ATT_TIME = "time"
    IMPORT_PROCESS_ATT_USER = "user"
    IMPORT_PROCESS_ATT_IP = "ip"
    IMPORT_PROCESS_ATT_DATASOURCE_PREFIX = "http://landportal.info/ontology/dataSource/"
    IMPORT_PROCESS_ATT_TYPE_PREFIX = "http://landportal.info/ontology/importProcess/"
    IMPORT_PROCESS_ATT_USER_PREFIX = "http://landportal.info/ontology/user/"
    #IMPORT_PROCESS_ATT_TIME_PREFIX = NO PREFIX FOR TIME
    '''
    classdocs
    '''


    def __init__(self, dataset, import_type):
        self.dataset = dataset
        self.import_type = import_type
        
        '''
        Constructor
        '''
    
    def run(self):
        self.build_root()
        self.build_import_process_node()
        self.build_indicators_node()
        self.build_dataset()
        
        self.write_tree_to_xml()
        
    def build_indicators_node(self):
        self.root.append(Element(self.INDICATORS))
        #No further actions needed. Nodes <indicator>
        #should be included to this while parsing
        #observations
        
    def write_tree_to_xml(self):
        ElementTree(self.root).write("file.xml")
        
    def build_root(self):
        self.root = Element(self.ROOT)
        
    def build_dataset(self):
        for data_slice in self.dataset.slices:
            self.root.append(self.build_slice(data_slice))
            
#         for data_sli in self.dataset.slices:
#             a_slice_node = Element(self.SLICE)
#             a_slice_node.attrib[self.SLICE_ATT_ID] = data_sli.slice_id
#             self.root.append(a_slice_node)
#             self.build_slice(a_slice_node, data_sli)
    
    def build_slice(self, a_slice_node, data_slice):
        a_slice_node = Element(self.SLICE)
        self.add_att_to_slice(a_slice_node, data_slice)
#         for data_obs in data_slice.observations:
#             a_observation_node = self.build_observation(data_obs)
#             a_slice_node.append(a_observation_node)
            

#             aObservationNode[self.OBSERVATION_ATT_ID] = obs.observation_id
#             self.build_observation(obs)
            
    def add_att_to_slice(self, a_slice_node, data_slice):
        a_slice_node.attrib[self.SLICE_ATT_ID] = \
                        data_slice.slice_id
            
        pass
    def build_observation(self, data_obs):
        
        result = Element(self.OBSERVATION)
        result.attrib[self.OBSERVATION_ATT_ID] = \
                        str(data_obs.observation_id)
        result.attrib[self.OBSERVATION_ATT_COUNTRY] = \
                        self.OBSERVATION_ATT_COUNTRY_PREFIX \
                        + str(data_obs.region.name)
        result.attrib[self.OBSERVATION_ATT_VALUE] = \
                        str(data_obs.value.value)
        result.attrib[self.OBSERVATION_ATT_MEASURE] = \
                        self.OBSERVATION_ATT_MEASURE_PREFIX \
                        + str(data_obs.measure_unit.name)
        result.attrib[self.OBSERVATION_ATT_INDICATOR] = \
                        self.OBSERVATION_ATT_INDICATOR_PREFIX \
                        + str(data_obs.indicator.name)
        result.attrib[self.OBSERVATION_ATT_TIME] = \
                        self.OBSERVATION_ATT_TIME_PREFIX \
                        + str(data_obs.ref_time.time)
#         result[self.OBSERVATION_ATT_RELATED] = 
#         result[self.OBSERVATION_ATT_RELATION_PROPERTY] = 
        return result
    
    def build_import_process_node(self):
        metadata = Element(self.IMPORT_PROCESS)
        metadata.attrib[self.IMPORT_PROCESS_ATT_DATASOURCE] = \
                        self.IMPORT_PROCESS_ATT_DATASOURCE_PREFIX \
                        + self.dataset.source.source_id
                        
        metadata.attrib[self.IMPORT_PROCESS_ATT_TYPE] = \
                        self.IMPORT_PROCESS_ATT_TYPE_PREFIX \
                        + self.import_type
                        
        metadata.attrib[self.IMPORT_PROCESS_ATT_TIME] = \
                        self.dataset.data_source.organization.user.timestamp
                                    
        metadata.attrib[self.IMPORT_PROCESS_ATT_USER] = \
                        self.IMPORT_PROCESS_ATT_USER_PREFIX \
                        + self.dataset.data_source.organization.user.user_id
                        
        metadata.attrib[self.IMPORT_PROCESS_ATT_IP] = \
                        self.dataset.data_source.organization.user.ip
        self.root.append(metadata)
        
        
               
        
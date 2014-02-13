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
    SLICE = "slice"
    SLICE_ATT_ID = "id"
    OBSERVATIONS = "observations"
    
    
    OBSERVATION = "observation"
    OBSERVATION_ATT_ID = "id"
    OBSERVATION_ATT_ISSUED = "issued"
    OBSERVATION_ATT_OBS_STATUS = "obs-status"
    OBSERVATION_ATT_COMPUTATION = "computation"
    OBSERVATION_ATT_COUNTRY = "country"
    OBSERVATION_ATT_VALUE = "value"
    OBSERVATION_ATT_INDICATOR = "indicator"
    OBSERVATION_ATT_TIME = "time"
    OBSERVATION_ATT_RELATED = "relatedObs"
    OBSERVATION_ATT_RELATION_PROPERTY = "relationProperty"
    
    OBSERVATION_ATT_COUNTRY_PREFIX = "http://landportal.info/ontology/country/"
    OBSERVATION_ATT_INDICATOR_PREFIX = "http://landportal.info/ontology/country/indicator/"
    OBSERVATION_ATT_TIME_PREFIX = "http://landportal.info/ontology/year/"
    OBSERVATION_ATT_RELATION_PROPERTY_PREFIX = "http://landportal.info/ontology/relation/"
    
    
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
    
    INDICATOR = "indicator"
    INDICATOR_ATT_ID = "id"
    INDICATOR_ATT_NAME = "name"
    INDICATOR_ATT_DESCRIPTION = "description"
    INDICATOR_ATT_MEASURE_UNIT  = "measure_unit"
    
    INDICATOR_ATT_ID_PREFIX = "http://landportal.info/ontology/country/indicator/"
    INDICATOR_ATT_MEASURE_UNIT_PREFIX = "http://landportal.info/ontology/country/currency/"
    
    LICENSE = "license"
    LICENSE_ATT_NAME = "name"
    LICENSE_ATT_DESCRIPTION = "description"
    LICENSE_ATT_REPUBLISH = "republish"
    LICENSE_ATT_URL = "republish"
    '''
    classdocs
    '''


    def __init__(self, dataset, import_type):
        self.datasource = dataset.source
        self.dataset = dataset
        self.import_type = import_type
        self.indicator_dic = {} #It will store an indicator object with it id as key.
                                #One per indicator referred by the observations
        
        '''
        Constructor
        '''
    
    def run(self):
        self.build_root()
        self.build_import_process_node()
        self.build_observations_node()
        self.build_indicators_node()
        self.build_slices_node()
        
        self.write_tree_to_xml()
      
      
    def build_observations_node(self):
        observations_node = Element(self.OBSERVATIONS)
        for data_obs in self.datasource.observations:
            observations_node.append(self.build_observation_node(data_obs))
        self.root.append(observations_node)
        
      
    def build_indicators_node(self):
        result = Element(self.INDICATORS)
        for data_indicator in self.indicator_dic:
            result.append(self.build_indicator_node(data_indicator))
        
        #No further actions needed. Nodes <indicator>
        #should be included to this while parsing
        #observations
        self.root.append(result)
        
    def build_indicator_node(self, data_indicator):
        #Building node
        result = Element(self.INDICATOR)
        
        #Attaching attribs
        #id name description measureUnit
        result.attrib[self.INDICATOR_ATT_ID] = \
                self.INDICATOR_ATT_ID_PREFIX \
                + data_indicator.indicator_id
        result.attrib[self.INDICATOR_ATT_NAME] = \
                data_indicator.name
        result.attrib[self.INDICATOR_ATT_DESCRIPTION] = \
                data_indicator.description
        result.attrib[self.INDICATOR_ATT_MEASURE_UNIT] = \
                self.INDICATOR_ATT_MEASURE_UNIT_PREFIX \
                + data_indicator.measure_unit
        
        #Adding license node
        result.append(self.build_license_node(data_indicator.license))
        
        #Returning complete node
        return result
        
    def build_license_node(self, data_indicator):
        #Building node
        result = Element(self.LICENSE)
        
        #Attaching atts.
        #name description republish url
        result.attrib[self.LICENSE_ATT_NAME] = data_indicator.name
        result.attrib[self.LICENSE_ATT_DESCRIPTION] = data_indicator.description
        result.attrib[self.LICENSE_ATT_REPUBLISH] = data_indicator.republish
        result.attrib[self.LICENSE_ATT_URL] = data_indicator.url
        
        #Returning complete node
        return result
        
    
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
  
    
    
    def build_observation_node(self, data_obs):
        #Building node
        result = Element(self.OBSERVATION)
        
        #Attaching attributes
        #id, issued, (obs-status, value), computation, country, time, indicator, (related-obs, related-prop)
        result.attrib[self.OBSERVATION_ATT_ID] = \
                        str(data_obs.observation_id)
        result.attrib[self.OBSERVATION_ATT_ISSUED] = \
                        data_obs.issued.get_time_string()
        result.attrib[self.OBSERVATION_ATT_COMPUTATION] = \
                        + data_obs.computation.uri                                        
        result.attrib[self.OBSERVATION_ATT_COUNTRY] = \
                        self.OBSERVATION_ATT_COUNTRY_PREFIX \
                        + str(data_obs.region.iso3)
        result.attrib[self.OBSERVATION_ATT_TIME] = \
                        self.OBSERVATION_ATT_TIME_PREFIX \
                        + str(data_obs.ref_time.time)   
        #Attaching value properties
        self.attach_value_att_to_observation(result, data_obs)
        
        #Managing indicator´s info
        result.attrib[self.OBSERVATION_ATT_INDICATOR] = \
                        self.OBSERVATION_ATT_INDICATOR_PREFIX \
                        + str(data_obs.indicator.indicator_id)
        self.include_indicator_if_needed(data_obs.indicator)
        
        #Attaching optional info
        self.attach_related_obs_info_to_observation(result, data_obs)

        #Returning the builded node  
        return result
    
    def attach_related_obs_info_to_observation(self,node_obs, data_obs):
        if(data_obs.is_related_to == None):
            return
        node_obs.attrib[self.OBSERVATION_ATT_RELATED] = \
                self.OBSERVATION_ATT_ID \
                + data_obs.is_related_to.observation_id
        node_obs.attrib[self.OBSERVATION_ATT_RELATION_PROPERTY] = \
                self.OBSERVATION_ATT_RELATION_PROPERTY_PREFIX \
                + data_obs.is_related_to.indicator.indicator_id
        #We could try to include the previous indicator in the list if needed,
        #in the same way we do when attaching indicator property in an <indicator>
        #node, but we are suppousing that if there is a related obs, it indicator
        #will be including quen treating that obs
        
        #No return sentence. We are modifying the received object
        pass
    
    def include_indicator_if_needed(self, data_indicator):
        if(self.indicator_dic.has_key(data_indicator.indicator_id)):
            return
        self.indicator_dic[data_indicator.indicator_id] = data_indicator
        pass
    
    def attach_value_att_to_observation(self, obs_node, data_obs):
        #Adding obligatory att obs-status
        status = data_obs.value.obs_status
        obs_node.attrib[self.OBSERVATION_ATT_OBS_STATUS] = status
        
        #Adding value if needed
        if not status == data_obs.value.MISSING:
            obs_node.attrib[self.OBSERVATION_ATT_VALUE] = \
                    str(data_obs.value.value)
        #No return sentence. We are modifying the received obs_node object
    
    def build_import_process_node(self):
        #Building node
        metadata = Element(self.IMPORT_PROCESS)
        
        #Attaching attributes
        metadata.attrib[self.IMPORT_PROCESS_ATT_DATASOURCE] = \
                        self.IMPORT_PROCESS_ATT_DATASOURCE_PREFIX \
                        + self.datasource.name
                        
        metadata.attrib[self.IMPORT_PROCESS_ATT_TYPE] = \
                        self.IMPORT_PROCESS_ATT_TYPE_PREFIX \
                        + self.import_type
                        
        metadata.attrib[self.IMPORT_PROCESS_ATT_TIME] = \
                        self.datasource.organization.user.timestamp
                                    
        metadata.attrib[self.IMPORT_PROCESS_ATT_USER] = \
                        self.IMPORT_PROCESS_ATT_USER_PREFIX \
                        + self.datasource.organization.user.user_id
                        
        metadata.attrib[self.IMPORT_PROCESS_ATT_IP] = \
                        self.datasource.organization.user.ip
        #Addind node to root
        self.root.append(metadata)
     
        
# coding=utf-8
"""
Created on 03/02/2014

@author: Dani
"""
from __future__ import unicode_literals

try:
    from xml.etree.cElementTree import Element, ElementTree
except:
    from xml.etree.ElementTree import Element, ElementTree
from lpentities.interval import Interval
from lpentities.instant import Instant
from lpentities.month_interval import MonthInterval
from lpentities.year_interval import YearInterval
from lpentities.time import Time
from lpentities.region import Region


class ModelToXMLTransformer(object):
    #
    # Const containing names of tag or attributtes
    # to use in the XML file
    #
    ROOT = "dataset"
    INDICATORS = "indicators"

    SLICES = "slices"
    SLICE = "slice"
    SLICE_METADATA = "sli_metadata"
    SLICE_ATT_ID = "id"
    SLICE_REFERRED = "referred"

    OBSERVATIONS = "observations"

    OBSERVATION = "observation"
    OBSERVATION_ATT_ID = "id"
    OBSERVATION_ISSUED = "issued"
    OBSERVATION_OBS_STATUS = "obs-status"
    OBSERVATION_COMPUTATION = "computation"
    OBSERVATION_REGION = "region"
    OBSERVATION_VALUE = "value"
    OBSERVATION_INDICATOR = "indicator"
    OBSERVATION_TIME = "time"
    OBSERVATION_ATT_GROUP = "group"

    OBSERVATION_ATT_COUNTRY_PREFIX = ""  # Empty value, but it remains here because it could still be changed
    OBSERVATION_ATT_INDICATOR_PREFIX = ""  # Empty value, but it remains here because it could still be changed
    OBSERVATION_ATT_TIME_PREFIX = ""  # Empty value, but it remains here because it could still be changed

    IMPORT_PROCESS = "import_process"
    IMPORT_PROCESS_ORGANIZATION_NAME = "organization_name"
    IMPORT_PROCESS_ORGANIZATION_URL = "organization_url"
    IMPORT_PROCESS_DATASOURCE = "datasource"
    IMPORT_PROCESS_TYPE = "type"
    IMPORT_PROCESS_TIMESTAMP = "timestamp"
    IMPORT_PROCESS_USER = "user"
    IMPORT_PROCESS_SDMX_FREQUENCY = "sdmx_frequency"
    IMPORT_PROCESS_DATASOURCE_PREFIX = ""  # Empty value, but it remains here because it could still be changed
    IMPORT_PROCESS_TYPE_PREFIX = ""  # Empty value, but it remains here because it could still be changed
    IMPORT_PROCESS_USER_PREFIX = ""  # Empty value, but it remains here because it could still be changed

    INDICATOR = "indicator"
    INDICATOR_ATT_ID = "id"
    INDICATOR_NAME_EN = "ind_name_en"
    INDICATOR_NAME_ES = "ind_name_es"
    INDICATOR_NAME_FR = "ind_name_fr"
    INDICATOR_DESCRIPTION_EN = "ind_description_en"
    INDICATOR_DESCRIPTION_ES = "ind_description_es"
    INDICATOR_DESCRIPTION_FR = "ind_description_fr"
    INDICATOR_MEASURE_UNIT = "measure_unit"
    INDICATOR_TOPIC = "topic-ref"
    INDICATOR_SPLITS_IN = "splitsIn"
    INDICATOR_PREFERABLE_TENDENCY = "preferable_tendency"

    INDICATOR_REF = "indicator-ref"

    INDICATOR_ATT_ID_PREFIX = ""  # Empty value, but it remains here because it could still be changed
    INDICATOR_ATT_MEASURE_UNIT_PREFIX = ""  # Empty value, but it remains here because it could still be changed

    LICENSE = "license"
    LICENSE_NAME = "lic_name"
    LICENSE_DESCRIPTION = "lic_description"
    LICENSE_REPUBLISH = "republish"
    LICENSE_URL = "lic_url"

    TIME = "time"
    TIME_INTERVAL = "interval"
    TIME_INTERVAL_BEG = "beginning"
    TIME_INTERVAL_END = "end"
    TIME_ATT_UNIT = "unit"

    INDICATOR_GROUPS = "indicator_groups"
    GROUP = "indicator_group"
    GROUP_ATT_ID = "id"
    GROUP_ATT_INDICATOR = "indicator"

    OBSERVATION_REF = "observation-ref"
    OBSERVATION_REF_ID = "id"
    '''
    classdocs
    '''


    def __init__(self, dataset, import_process, user, indicator_relations=None):
        self.datasource = dataset.source
        self.dataset = dataset
        self.user = user
        self.import_process = import_process
        self.root = None
        self.indicator_dic = {}  # It will store an indicator object with it id as key.
        self.group_dic = {}
        self.indicator_relations = indicator_relations
        # One per indicator referred by the observations

        self.root = Element(self.ROOT)

        '''
        Constructor
        '''

    def run(self):
        #The order calling these methods should not be changed
        self.build_import_process_node()  # Done
        self.build_license_node()  # Done
        self.build_observations_node()  # Done
        self.build_indicators_node()  # Done
        self.build_indicator_groups_node()  # Done
        self.build_slices_node()  # Done
        self.include_indicator_relations()  # Done? TODO: UNTESTED
        self.write_tree_to_xml()  # PROVISIONAL. The final task y consuming web service, not writing


    def include_indicator_relations(self):
        if self.indicator_relations is None or len(self.indicator_relations) == 0:
            return  # Nothing to fo (most of cases)
        else:
            for a_relation in self.indicator_relations:
                self.include_relation_in_the_tree(a_relation)

    def include_relation_in_the_tree(self, a_relation):
        #Looking for source node in the tree
        source_node = self._get_indicator_node_by_id(a_relation.source.indicator_id)
        relations_node = source_node.find(self.INDICATOR_SPLITS_IN)

        #Creating base relation node if needed, and incorporating it to the tree
        if relations_node is None:
            relations_node = Element(self.INDICATOR_SPLITS_IN)
            source_node.append(relations_node)

        #Creating and adding new relation
        new_node = Element(self.INDICATOR_REF)
        new_node.text = a_relation.target.indicator_id
        source_node.append(new_node)


    def _get_indicator_node_by_id(self, indicator_id):
        indicator_nodes= self.root.find(self.INDICATORS).getchildren()
        for ind in indicator_nodes:
            if ind[self.INDICATOR_ATT_ID] == indicator_id:
                return ind
        raise RuntimeError("Impossible to find indicator with id {0}. Unable to relate indicators with it"
                           .format(indicator_id))

    def build_indicator_groups_node(self):
        groups = Element(self.INDICATOR_GROUPS)
        for group_node in self.group_dic:
            # The nodes are already built. We are storing nodes in the dict
            groups.append(group_node)
        self.root.append(groups)

    def build_slices_node(self):
        #Building node
        slices_node = Element(self.SLICES)
        #Building child nodes
        for data_slice in self.dataset.slices:
            slices_node.append(self.build_slice_node(data_slice))
        #Appending node to root
        self.root.append(slices_node)


    def build_slice_node(self, data_slice):
        #Building node
        slice_node = Element(self.SLICE)
        #Attaching info
        #id
        slice_node.attrib[self.SLICE_ATT_ID] = data_slice.slice_id
        #metadata
        slice_node.append(self.build_metadata_slice_node(data_slice))
        #referred obs
        slice_node.append(self.build_referred_slice_node(data_slice))
        #returnin node
        return slice_node


    def build_metadata_slice_node(self, data_slice):
        #Building metadata
        metadata_node = Element(self.SLICE_METADATA)
        #Adding info
        #indicator-ref
        indicator_ref_node = Element(self.INDICATOR_REF)
        indicator_ref_node.attrib[self.INDICATOR_ATT_ID] = data_slice.indicator.indicator_id
        metadata_node.append(indicator_ref_node)

        #time/region
        if isinstance(data_slice.dimension, Time):
            metadata_node.append(self.build_time_node(data_slice.dimension))
        elif isinstance(data_slice.dimension, Region):
            region_node = Element(self.OBSERVATION_REGION)
            region_node.text = self.OBSERVATION_ATT_COUNTRY_PREFIX \
                               + data_slice.dimension.un_code
            metadata_node.append(region_node)

        else:
            raise RuntimeError("Unknown dimension while building slice.")

        #Returnin node
        return metadata_node

    def build_referred_slice_node(self, data_slice):
        #Building node
        referred_node = Element(self.SLICE_REFERRED)

        #Adding info
        for data_obs in data_slice.observations:
            obs_node = Element(self.OBSERVATION_REF)
            obs_node.attrib[self.OBSERVATION_ATT_ID] = data_obs.observation_id
            referred_node.append(obs_node)
        #returnig node
        return referred_node


    def build_observations_node(self):
        observations_node = Element(self.OBSERVATIONS)
        for data_obs in self.dataset.observations:
            observations_node.append(self.build_observation_node(data_obs))
        self.root.append(observations_node)


    def build_indicators_node(self):
        result = Element(self.INDICATORS)
        for data_indicator in self.indicator_dic:
            result.append(self.build_indicator_node(self.indicator_dic[data_indicator]))

        self.root.append(result)

    def build_indicator_node(self, data_indicator):
        #Building node
        result = Element(self.INDICATOR)

        #Attaching info
        #id
        result.attrib[self.INDICATOR_ATT_ID] = \
            self.INDICATOR_ATT_ID_PREFIX \
            + data_indicator.indicator_id
        #names
        names = self._extract_indicator_name_nodes(data_indicator)
        for a_name in names:
            result.append(a_name)

        #descriptions
        descriptions = self._extract_indicator_description_nodes(data_indicator)
        for a_desc in descriptions:
            result.append(a_desc)

        #topic
        node_topic = Element(self.INDICATOR_TOPIC)
        node_topic.text = data_indicator.topic
        result.append(node_topic)

        #preferable_tendency
        node_tendency = Element(self.INDICATOR_PREFERABLE_TENDENCY)
        node_tendency.text = data_indicator.preferable_tendency
        result.append(node_tendency)

        #MeasureUnit
        node_measure = Element(self.INDICATOR_MEASURE_UNIT)
        node_measure.text = self.INDICATOR_ATT_MEASURE_UNIT_PREFIX \
                            + data_indicator.measurement_unit.name
        result.append(node_measure)

        #Returning complete node
        return result

    def _extract_indicator_description_nodes(self, data_indicator):
        result = []

        #EN
        node_desc_en = Element(self.INDICATOR_DESCRIPTION_EN)
        node_desc_en.text = data_indicator.description_en
        result.append(node_desc_en)
        #ES
        node_desc_es = Element(self.INDICATOR_DESCRIPTION_ES)
        node_desc_es.text = data_indicator.description_es
        result.append(node_desc_es)
        #FR
        node_desc_fr = Element(self.INDICATOR_DESCRIPTION_FR)
        node_desc_fr.text = data_indicator.description_fr
        result.append(node_desc_fr)

        return result

    def _extract_indicator_name_nodes(self, data_indicator):
        result = []
        #EN
        node_name_en = Element(self.INDICATOR_NAME_EN)
        node_name_en.text = data_indicator.name_en
        result.append(node_name_en)
        #ES
        node_name_es = Element(self.INDICATOR_NAME_ES)
        node_name_es.text = data_indicator.name_es
        result.append(node_name_es)
        #FR
        node_name_fr = Element(self.INDICATOR_NAME_FR)
        node_name_fr.text = data_indicator.name_fr
        result.append(node_name_fr)

        return result

    def build_license_node(self):
        #Building node
        license_node = Element(self.LICENSE)

        #Attaching info
        #name
        name_node = Element(self.LICENSE_NAME)
        name_node.text = self.dataset.license_type.name
        license_node.append(name_node)

        #description
        desc_node = Element(self.LICENSE_DESCRIPTION)
        desc_node.text = self.dataset.license_type.description
        license_node.append(desc_node)

        #republish
        republish_node = Element(self.LICENSE_REPUBLISH)
        republish_node.text = str(self.dataset.license_type.republish)
        license_node.append(republish_node)

        #url
        url_node = Element(self.LICENSE_URL)
        url_node.text = self.dataset.license_type.url
        license_node.append(url_node)


        #Attaching node to root
        self.root.append(license_node)


    def write_tree_to_xml(self):

            ElementTree(self.root).write("file.xml", encoding="utf-8")



    def build_observation_node(self, data_obs):
        #Building node
        observation_node = Element(self.OBSERVATION)

        #Attaching info
        #id (attrib.)
        observation_node.attrib[self.OBSERVATION_ATT_ID] = \
            str(data_obs.observation_id)
        #issued
        issued_node = Element(self.OBSERVATION_ISSUED)
        issued_node.text = data_obs.issued.get_time_string()
        observation_node.append(issued_node)
        #obs-staus, value
        self.attach_value_to_observation(observation_node, data_obs)

        #computation
        computation_node = Element(self.OBSERVATION_COMPUTATION)
        computation_node.text = data_obs.computation.uri
        observation_node.append(computation_node)

        #region
        country_node = Element(self.OBSERVATION_REGION)
        country_node.text = self.OBSERVATION_ATT_COUNTRY_PREFIX \
                            + str(data_obs.region.un_code)

        observation_node.append(country_node)

        #time
        observation_node.append(self.build_time_node(data_obs.ref_time))

        #indicator
        indicator_ref_node = Element(self.INDICATOR_REF)
        indicator_ref_node.attrib[self.OBSERVATION_INDICATOR] = \
            self.OBSERVATION_ATT_INDICATOR_PREFIX \
            + str(data_obs.indicator.indicator_id)
        self.include_indicator_if_needed(data_obs.indicator)  # Managing ind. info
        observation_node.append(indicator_ref_node)

        #Attaching optional group info
        self.attach_groups_info_if_needed(observation_node, data_obs)

        return observation_node


    def build_time_node(self, ref_time):
        #Building top node
        time_node = Element(self.TIME)

        #Managging different time instances
        if type(ref_time) is Instant:
            time_node.attrib[self.TIME_ATT_UNIT] = "instant"
            time_node.text = ref_time.get_time_string()
        elif type(ref_time) is YearInterval:
            time_node.attrib[self.TIME_ATT_UNIT] = "years"
            time_node.text = ref_time.get_time_string()
        elif type(ref_time) is MonthInterval:
            time_node.attrib[self.TIME_ATT_UNIT] = "months"
            time_node.text = ref_time.get_time_string()
        elif type(ref_time) is Interval:
            time_node.attrib[self.TIME_ATT_UNIT] = "years"
            interval_node = Element(self.TIME_INTERVAL)
            beg_node = Element(self.TIME_INTERVAL_BEG)
            beg_node.text = str(ref_time.start_time)
            end_node = Element(self.TIME_INTERVAL_END)
            end_node.text = str(ref_time.end_time)
            interval_node.append(beg_node)
            interval_node.append(end_node)
            time_node.append(interval_node)
        else:
            raise RuntimeError("Unrecognized time type. Impossible to build node")
        #Returning final node
        return time_node


    def attach_groups_info_if_needed(self, node_obs, data_obs):
        if data_obs.indicator_group is None:
            return  # No actions needed in this case
        node_obs.attrib[self.OBSERVATION_ATT_GROUP] = data_obs.indicator_group.group_id
        self.treat_new_group_info(data_obs.indicator_group)

    def treat_new_group_info(self, data_obs):
        data_group = data_obs.indicator_group
        #Treating indicator info
        self.include_indicator_if_needed(data_group)  # Group info is a specialization of indicator

        #Treating group_node info
        group_node = None
        #Looking for node/adding node to internal dict if needed
        if data_group.group_id in self.group_dic:
            group_node = self.group_dic[data_group.group_id]
        else:
            group_node = Element(self.GROUP)
            group_node.attrib[self.GROUP_ATT_ID] = str(data_group.group_id)
            group_node.attrib[self.GROUP_ATT_INDICATOR] = \
                self.INDICATOR_ATT_ID_PREFIX + data_group.indicator_id
            self.group_dic[data_group.group_id] = group_node

        # We don't need to add observations to this node according to the current spec. but it could change.
        # So code for that remains in this comment
        #
        # #Adding obs to node
        # obs_node_ref = Element(self.OBSERVATION_REF)
        # obs_node_ref.attrib[self.OBSERVATION_REF_ID] = data_obs.observation_id
        # group_node.append(obs_node_ref)

    def include_indicator_if_needed(self, data_indicator):
        if data_indicator.indicator_id in self.indicator_dic:
            return
        self.indicator_dic[data_indicator.indicator_id] = data_indicator

    def attach_value_to_observation(self, obs_node, data_obs):
        #Adding obligatory node obs-status
        status_node = Element(self.OBSERVATION_OBS_STATUS)
        status = data_obs.value.obs_status
        status_node.text = status
        obs_node.append(status_node)

        #Adding value if needed
        if not status == data_obs.value.MISSING:
            value_node = Element(self.OBSERVATION_VALUE)
            value_node.text = str(data_obs.value.value)
            obs_node.append(value_node)

            #No returning sentence. We are modifying the received obs_node object

    def build_import_process_node(self):
        #Building node
        metadata = Element(self.IMPORT_PROCESS)

        #Attaching nodes
        #Organization_name
        organization_name_node = Element(self.IMPORT_PROCESS_ORGANIZATION_NAME)
        organization_name_node.text = self.datasource.organization.name
        metadata.append(organization_name_node)
        #Organization_url
        organization_url_node = Element(self.IMPORT_PROCESS_ORGANIZATION_URL)
        organization_url_node.text = self.datasource.organization.url
        metadata.append(organization_url_node)

        #datasource
        datasource_node = Element(self.IMPORT_PROCESS_DATASOURCE)
        datasource_node.text = self.IMPORT_PROCESS_DATASOURCE_PREFIX \
                               + self.datasource.name
        metadata.append(datasource_node)

        #type
        type_node = Element(self.IMPORT_PROCESS_TYPE)
        type_node.text = self.IMPORT_PROCESS_TYPE_PREFIX \
                         + self.import_process
        metadata.append(type_node)

        #user
        user_node = Element(self.IMPORT_PROCESS_USER)
        user_node.text = self.IMPORT_PROCESS_USER_PREFIX \
                         + self.user.user_id
        metadata.append(user_node)
        #sdmx_frequency
        sdmx_freq_node = Element(self.IMPORT_PROCESS_SDMX_FREQUENCY)
        sdmx_freq_node.text = self.dataset.frequency
        metadata.append(sdmx_freq_node)


        #Addind node to root
        self.root.append(metadata)

    @staticmethod
    def _read_external_field(original):
        try:
            return unicode(original, errors="ignore")
        except:
            return original
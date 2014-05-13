from ConfigParser import ConfigParser
import logging

from weso.raw.importer.raw_importer import RawImporter


__author__ = 'BorjaGB'


def update_ini_file(importer, config, config_path):
    print "Updating ini file"
    try:
        config.add_section(importer._indicator.name_en)
    except:
        pass
    
    try:
        config.set(importer._indicator.name_en, "id", importer.custom_ind_int)
        config.set(importer._indicator.name_en, "dataset", importer.custom_dat_int)
    except:
        config.set(importer._indicator.name_en, "id", importer._ind_int)
        config.set(importer._indicator.name_en, "dataset", importer._dat_int)
    
    config.set("TRANSLATOR", "ind_int", importer._ind_int)
    config.set("TRANSLATOR", 'obs_int', importer._obs_int)
    config.set("TRANSLATOR", 'sli_int', importer._sli_int)
    config.set("TRANSLATOR", 'dat_int', importer._dat_int)
    config.set("TRANSLATOR", 'igr_int', importer._igr_int)
    with open(config_path, 'wb') as configfile:
        config.write(configfile)

def configure_log():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='rawimporter.log', level=logging.INFO,
                        format=FORMAT)

def run():
    configure_log()
    log = logging.getLogger("rawimporter")
    
    try:
        config_path = "../../../files/"
        config_file_path = format_custom_ini_file_name(config_path, "configuration.ini")
        config = ConfigParser()
        config.read(config_file_path)
    
        organizations = dict(config.items("ORGANIZATIONS"))
    
        for org_id in organizations:
    
            files = organizations[org_id].split(",")
            custom_config_path = format_custom_ini_file_name(config_path, org_id.strip())
            print "Working with %s files"%org_id
            for file_name in files:
                try:
                    config.read(custom_config_path)
                except:
                    config.read(config_file_path) # Reload config
                    
                raw_importer = RawImporter(log, config, org_id, file_name.strip(), config.getboolean("TRANSLATOR", "historical_mode"))
                raw_importer.run()
                
                update_ini_file(raw_importer, config, custom_config_path)
                print "Done with %s"%file_name
            
    except Exception as detail:
        print "OOOOOPS! %s" %detail
        
    print "Done!"

def format_custom_ini_file_name(config_path, file_name):
    ext = file_name.rfind(".")
    if file_name.endswith(".ini"):
        return config_path + file_name
    elif ext == -1:
        return config_path + file_name + ".ini"
    else:
        ext = file_name.rfind(".")
        return config_path + file_name[:ext+1] + "ini"
    
if __name__ == '__main__':
    run()

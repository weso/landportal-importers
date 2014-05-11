from ConfigParser import ConfigParser
import logging

from weso.raw.importer.raw_importer import RawImporter


__author__ = 'BorjaGB'


def update_ini_file(importer, config, config_path):
    print "Updating ini file"
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
    config_path = "../../../files/configuration.ini"
    config = ConfigParser()
    config.read(config_path)

    organizations = dict(config.items("ORGANIZATIONS"))

    for org_id in organizations:
        files = organizations[org_id].split(",")
        print "Working with %s files"%org_id
        for file_name in files:
            raw_importer = RawImporter(log, config, org_id, file_name, config.getboolean("TRANSLATOR", "historical_mode"))
            raw_importer.run()
            
            update_ini_file(raw_importer, config, config_path)
            print "Done with %s"%file_name

    print "Done!"

if __name__ == '__main__':
    run()

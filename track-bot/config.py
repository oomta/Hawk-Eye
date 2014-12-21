from google.appengine.api import lib_config
import yaml

CONFIGURATION_FILE = 'configuration'

app_globals = lib_config.register('config', yaml.load(open(CONFIGURATION_FILE, 'r').read()))
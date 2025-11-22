import configparser

config_parser = configparser.ConfigParser()
config_parser.read('sqlconfig.ini')

config = {key: config_parser.get('mysql', key) for key in ['host','user','password','database']}

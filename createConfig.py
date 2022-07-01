import configparser
config = configparser.ConfigParser()
# Connection for the user George
config['Stan'] = {'username': 'stanwong178@gmail.com',
                     'password': '4190L7A2o7'}

# write the 
with open('my_config.ini', 'w') as configfile:
    config.write(configfile)
import configparser
config = configparser.ConfigParser()
# Connection for the user George
config['your account name'] = {'username': 'your username',
                     'password': 'your password'}

# write the 
with open('my_config.ini', 'w') as configfile:
    config.write(configfile)

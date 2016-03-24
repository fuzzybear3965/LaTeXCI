from cryptography.fernet import Fernet
import ConfigParser
class Session:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read('app.cfg')
        f = Fernet(config.get('global','symkey'))
        self.token = f.decrypt(config.get('global','apikey'))

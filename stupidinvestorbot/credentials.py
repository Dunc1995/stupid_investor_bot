import json
from stupidinvestorbot import CREDENTIALS_PATH


class Credentials:
    '''
    Basic object for storing API credentials. Probably not secure.
    '''
    def __init__(self, key, secret_key):
        self.key = key
        self.secret_key = secret_key

def CredentialsDecoder(jsonDict) -> Credentials:
    '''
    Read dict to Credentials object.
    '''
    return Credentials(jsonDict["key"],jsonDict["secret_key"])

def read_api_credentials() -> Credentials:
    '''
    Attempts to generate a Credentials object assuming that a credentials file exists.

    TODO - Encrypt credentials file.
    '''
    output = None

    with open(CREDENTIALS_PATH, 'r') as f:
            output = json.loads(f.read(), object_hook=CredentialsDecoder)
    
    return output
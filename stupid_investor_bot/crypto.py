import hmac
import hashlib
import time
import requests
from stupid_investor_bot.credentials import Credentials

class CryptoClient:
    def __init__(self, rest_api : str, credentials : Credentials) -> None:
        self.credentials = credentials
        self.rest_api = rest_api
    
    def show_balance(self):
        req = {
            "id": 11,
            "method": "private/get-accounts",
            "api_key": self.credentials.key,
            "params": {},
            "nonce": int(time.time() * 1000)
        }

        # First ensure the params are alphabetically sorted by key
        param_str = ""

        MAX_LEVEL = 3


        def params_to_str(obj, level):
            if level >= MAX_LEVEL:
                return str(obj)

            return_str = ""
            for key in sorted(obj):
                return_str += key
                if obj[key] is None:
                    return_str += 'null'
                elif isinstance(obj[key], list):
                    for subObj in obj[key]:
                        return_str += params_to_str(subObj, level + 1)
                else:
                    return_str += str(obj[key])
            return return_str


        if "params" in req:
            param_str = params_to_str(req['params'], 0)

        payload_str = req['method'] + str(req['id']) + req['api_key'] + param_str + str(req['nonce'])

        req['sig'] = hmac.new(
            bytes(str(self.credentials.secret_key), 'utf-8'),
            msg=bytes(payload_str, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        headers = {'Content-Type': 'application/json'} 

        print(req)

        result = requests.post(self.rest_api + 'private/get-accounts', json=req, headers=headers)

        return result.text
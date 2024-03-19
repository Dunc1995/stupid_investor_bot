from dataclasses import dataclass
from dataclasses_json import dataclass_json
import hmac
import hashlib
import json
import time
import requests
import numpy
from stupidinvestorbot.credentials import Credentials

MAX_LEVEL = 3

def get_signature(req : dict, secret_key : str) -> str:
    # First ensure the params are alphabetically sorted by key
    param_str = ""

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

    return hmac.new(
        bytes(str(secret_key), 'utf-8'),
        msg=bytes(payload_str, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

@dataclass_json
@dataclass
class Ticker():
    instrument_name : str
    highest_trade_24h : str
    lowest_trade_24h : str
    latest_trade : str
    total_traded_volume_24h : str
    total_traded_volume_usd_24h : str
    percentage_change_24h : str
    best_bid_price : str
    best_ask_price : str
    open_interest : str
    timestamp : int

def ticker_decoder(obj : dict) -> Ticker:

    return Ticker(instrument_name = obj['i'],
    highest_trade_24h = obj['h'],
    lowest_trade_24h = obj['l'],
    latest_trade = obj['a'],
    total_traded_volume_24h = obj['v'],
    total_traded_volume_usd_24h = obj['vv'],
    percentage_change_24h = obj['c'],
    best_bid_price = obj['b'],
    best_ask_price = obj['k'],
    open_interest = obj['oi'],
    timestamp = obj['t'])

class CryptoClient:
    def __init__(self, rest_api : str, credentials : Credentials) -> None:
        self.credentials = credentials
        self.rest_api = rest_api
    
    def authorized_post_request(self, id : int, method : str, params = {}) -> str:
        req = {
            "id": id,
            "method": method,
            "api_key": self.credentials.key,
            "params": params,
            "nonce": int(time.time() * 1000)
        }

        req['sig'] = get_signature(req, self.credentials.secret_key)

        headers = {'Content-Type': 'application/json'} 

        result = requests.post(f'''{self.rest_api}{method}''', json=req, headers=headers)

        return result.text
    
    def user_balance(self) -> str:
        return self.authorized_post_request(1, 'private/user-balance')
    
    def get_volatile_coins(self) -> str:
        response = requests.get(f'''{self.rest_api}public/get-tickers''')
        
        data = [ ticker_decoder(obj) for obj in json.loads(response.text)['result']['data'] ]

        result = sorted(data, key=lambda x: tuple(x.percentage_change_24h))[-10:]

        return [ obj.to_dict() for obj in result ]
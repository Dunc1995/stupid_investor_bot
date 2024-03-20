import json
import requests
import stupidinvestorbot.auth as auth
from stupidinvestorbot import CRYPTO_REST_API
from stupidinvestorbot.models import Ticker

def user_balance() -> str:
    return auth.post_request(1, 'user-balance')


def get_top_ten_gaining_coins() -> list[Ticker]:
    response = requests.get(f'''{CRYPTO_REST_API}/public/get-tickers''')

    data = [ Ticker(obj) for obj in json.loads(response.text)['result']['data'] ]

    result = sorted(data, key=lambda x: tuple(x.percentage_change_24h))[-10:]

    return result
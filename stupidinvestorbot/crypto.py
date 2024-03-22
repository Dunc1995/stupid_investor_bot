import json
import requests
import datetime as dt
import time
import stupidinvestorbot.auth as auth
from stupidinvestorbot import CRYPTO_REST_API
from stupidinvestorbot.models import Ticker

api = lambda action: f"""{CRYPTO_REST_API}/public/{action}"""


def user_balance() -> str:
    return auth.post_request(1, "user-balance")


def get_highest_gain_coins(number_of_coins: int) -> list[Ticker]:
    response = requests.get(api("get-tickers"))

    data = [Ticker(obj) for obj in json.loads(response.text)["result"]["data"]]

    result = sorted(data, key=lambda x: tuple(x.percentage_change_24h))[
        -number_of_coins:
    ]

    return result


def get_valuation(instrument_name: str, valuation_type: str) -> dict:
    to_unix = lambda x: int(time.mktime(x.timetuple()) * 1000)

    date_now = to_unix(dt.datetime.now())
    date_past = to_unix(dt.datetime.now() - dt.timedelta(days=1))

    response = requests.get(
        api(
            f"""get-valuations?instrument_name={instrument_name}&valuation_type={valuation_type}&count=10000"""
        )
    )

    if response.status_code != 200:
        print(response.text)

        raise ValueError("Unable to process data")

    return json.loads(response.text)

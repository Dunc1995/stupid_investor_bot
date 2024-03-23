import json
import requests
from stupidinvestorbot.crypto import CRYPTO_REST_API
from stupidinvestorbot.models import Ticker

api = lambda action: f"""{CRYPTO_REST_API}/public/{action}"""


def get_highest_gain_coins(number_of_coins: int) -> list[Ticker]:
    response = requests.get(api("get-tickers"))

    data = [Ticker(obj) for obj in json.loads(response.text)["result"]["data"]]

    result = sorted(data, key=lambda x: tuple(x.percentage_change_24h))[
        -number_of_coins:
    ]  # TODO Add error handling here.

    return result


def get_instrument_summary(instrument_name: str) -> Ticker:
    """
    Get trading summary data for the input crypto currency name.
    """
    response = requests.get(api(f"""get-tickers?instrument_name={instrument_name}"""))

    data = [
        Ticker(obj) for obj in json.loads(response.text)["result"]["data"]
    ]  # TODO add error handling here.

    return data[0]


def get_valuation(instrument_name: str, valuation_type: str) -> dict:
    # ! start/end time query parameters don't seem to work hence the following being commented out
    # to_unix = lambda x: int(time.mktime(x.timetuple()) * 1000)

    # date_now = to_unix(dt.datetime.now())
    # date_past = to_unix(dt.datetime.now() - dt.timedelta(days=1))

    # * count query max ~4000 data points going back 24h
    # TODO attempt to retrieve data >24h ago.
    response = requests.get(
        api(
            f"""get-valuations?instrument_name={instrument_name}&valuation_type={valuation_type}&count=10000"""
        )
    )

    if response.status_code != 200:
        print(response.text)

        raise ValueError("Unable to process data")

    return json.loads(response.text)

from dataclasses import dataclass
import hashlib
import hmac
import json
import logging
import math
import time
import datetime as dt
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas import DataFrame
import requests
from stupidinvestorbot.transforms.models import CoinSummary, Ticker
from stupidinvestorbot.crypto.models import (
    Instrument,
    PositionBalance,
    UserBalance,
)
import stupidinvestorbot.transforms.quantities as quantities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")


@dataclass
class HttpClient:
    api_url: str

    def get(self, method: str):
        response = requests.get(f"{self.api_url}{method}")

        if response.status_code != 200:
            message = f"The following query did not succeed: ({self.api_url}{method})"

            logger.fatal(message, response.text)

            raise ValueError(message)

        return json.loads(response.text)

    def get_data(self, method: str):
        return self.get(method)["result"]["data"]


@dataclass
class AuthenticatedHttpClient(HttpClient):
    api_key: str
    api_secret_key: str

    def __params_to_str(self, obj, level):
        if level >= 3:  # ! level 3 seems to be arbitrarily chosen in crypto.com docs
            return str(obj)

        return_str = ""
        for key in sorted(obj):
            return_str += key
            if obj[key] is None:
                return_str += "null"
            elif isinstance(obj[key], list):
                for subObj in obj[key]:
                    return_str += self.__params_to_str(subObj, level + 1)
            else:
                return_str += str(obj[key])
        return return_str

    def __get_signature(self, req: dict) -> str:
        """
        See https://exchange-docs.crypto.com/exchange/v1/rest-ws/index.html#digital-signature
        """

        # First ensure the params are alphabetically sorted by key
        param_str = ""

        if "params" in req:
            param_str = self.__params_to_str(req["params"], 0)

        payload_str = (
            req["method"]
            + str(req["id"])
            + req["api_key"]
            + param_str
            + str(req["nonce"])
        )

        return hmac.new(
            bytes(str(self.api_secret_key), "utf-8"),
            msg=bytes(payload_str, "utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def post_request(self, id: int, method: str, params={}) -> Dict:
        req = {
            "id": id,
            "method": "private/" + method,
            "api_key": self.api_key,
            "params": params,
            "nonce": int(time.time() * 1000),
        }

        print("I got here with: " + json.dumps(req, indent=4))

        req["sig"] = self.__get_signature(req)

        headers = {"Content-Type": "application/json"}

        result = requests.post(f"{self.api_url}{method}", json=req, headers=headers)

        if result.status_code != 200:
            raise ValueError(result.text)

        return json.loads(result.text)["result"]["data"]


class MarketHttpClient(HttpClient):
    def __init__(
        self,
        api_url="https://api.crypto.com/exchange/v1/public/",
    ):
        super().__init__(api_url=api_url)

    def get_highest_gain_coins(self, number_of_coins: int) -> list[Ticker]:
        ticker_data = self.get_data("get-tickers")

        data = [Ticker(obj) for obj in ticker_data]

        result = sorted(data, key=lambda x: tuple(x.percentage_change_24h))[
            -number_of_coins:
        ]

        return result

    def get_instruments(self) -> List[Instrument]:
        instrument_data = self.get_data("get-instruments")

        data = [Instrument(**obj) for obj in instrument_data]

        return data

    def get_ticker(self, instrument_name: str) -> Ticker:
        ticker_data = self.get_data(f"get-tickers?instrument_name={instrument_name}")

        data = [Ticker(obj) for obj in ticker_data]

        return data[0]

    def get_valuation(self, instrument_name: str, valuation_type: str) -> dict:
        # ! start/end time query parameters don't seem to work hence the following being commented out
        # to_unix = lambda x: int(time.mktime(x.timetuple()) * 1000)

        # date_now = to_unix(dt.datetime.now())
        # date_past = to_unix(dt.datetime.now() - dt.timedelta(days=1))

        # * count query max ~4000 data points going back 24h
        # TODO attempt to retrieve data >24h ago.
        valuation_data = self.get_data(
            f"get-valuations?instrument_name={instrument_name}&valuation_type={valuation_type}&count=4000"
        )

        return valuation_data


class UserHttpClient(AuthenticatedHttpClient):
    def __init__(
        self,
        api_key,
        api_secret_key,
        api_url="https://api.crypto.com/exchange/v1/private/",
    ):
        super().__init__(
            api_key=api_key, api_secret_key=api_secret_key, api_url=api_url
        )

    def get_balance(self) -> Dict:
        return self.post_request(1, "user-balance")[
            0
        ]  # ! zero index assumes only one wallet - may break

    # ! TODO Streamline this
    def create_order(
        self,
        instrument_name: str,
        investment_total_usd: float,
        instrument_price_usd: float,
        quantity_tick: float,
        side: str,
    ):
        global buy_order_id
        print("Quantity increment is: " + quantity_tick)

        # TODO this needs fixing/testing - not foolproof
        quantity = quantities.get_coin_quantity(
            instrument_price_usd, investment_total_usd, quantity_tick
        )

        print(f"Total quantity is: {quantity}")
        print(f"Estimate order price (USD): {quantity*instrument_price_usd}")

        params = {
            "instrument_name": instrument_name,
            "side": side,
            "type": "LIMIT",
            "price": f"{instrument_price_usd}",
            "quantity": f"{quantity}",
            "time_in_force": "GOOD_TILL_CANCEL",
        }

        print(json.dumps(params, indent=4))

        result = self.post_request(buy_order_id, "create-order", params)

        buy_order_id += 1

        return result

    def get_open_orders(self, instrument_name=None):
        args = {} if instrument_name is None else {"instrument_name": instrument_name}

        return self.post_request(4, "get-open-orders", args)


class HttpClient:
    market: MarketHttpClient
    user: UserHttpClient

    def __init__(self, api_key, api_secret_key):
        self.market = MarketHttpClient()
        self.user = UserHttpClient(api_key, api_secret_key)

    @staticmethod
    def __get_coin_summary(coin: Ticker, valuation: DataFrame) -> CoinSummary:
        stats = valuation
        mean = stats["v"].mean()
        std = stats["v"].std()
        percentage_std = float(std) / float(mean)

        return CoinSummary(
            name=coin.instrument_name,
            latest_trade=float(coin.latest_trade),
            mean_24h=mean,
            std_24h=std,
            percentage_std_24h=percentage_std,
            is_greater_than_mean=bool(float(coin.latest_trade) - mean > 0),
            is_greater_than_std=bool(float(coin.latest_trade) - (mean + std) > 0),
        )

    def get_investment_increments(self):
        """
        Get my USD balance and calculate how many coins to invest in.
        """
        balance_dict = self.user.get_balance()

        balance = UserBalance(**balance_dict)

        usd_balance = next(
            (
                PositionBalance(**ub)
                for ub in balance.position_balances
                if PositionBalance(**ub).instrument_name == "USD"
            ),
            None,
        )

        total_investable = float(usd_balance.market_value)

        number_of_investments = math.floor(total_investable / 40.0)

        return total_investable, number_of_investments

    def get_coin_summaries(self, show_plots=False) -> List[CoinSummary]:
        output = []
        axs = None
        coin_number = 30
        i = 0
        coin_summaries = self.market.get_highest_gain_coins(coin_number)

        if show_plots:
            _, axs = plt.subplots(coin_number)

        for coin in coin_summaries:
            time_series_data = self.market.get_valuation(
                coin.instrument_name, "mark_price"
            )

            df = pd.DataFrame.from_dict(time_series_data)
            df["t"] = df["t"].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
            df["v"] = df["v"].astype(float)

            if show_plots:
                axs[i].plot(df["t"], df["v"])
                axs[i].set_title(coin.instrument_name)
                axs[i].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y"))

            output.append(HttpClient.__get_coin_summary(coin, df))

            i += 1

        if show_plots:
            plt.show()

        return output

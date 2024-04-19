import logging
import math
import datetime as dt
from typing import Any, Generator, List
import uuid
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas import DataFrame

from stupidinvestorbot.strategies import CoinSelection
import stupidinvestorbot.utils as utils
from stupidinvestorbot import INVESTMENT_INCREMENTS
from stupidinvestorbot.http.market import MarketHttpClient
from stupidinvestorbot.http.user import UserHttpClient
from stupidinvestorbot.models.app import CoinSummary, OrderSummary, Ticker
from stupidinvestorbot.models.crypto import Order, PositionBalance, UserBalance


logger = logging.getLogger("client")


class CryptoHttpClient:
    market: MarketHttpClient
    user: UserHttpClient

    def __init__(self, api_key, api_secret_key):
        self.market = MarketHttpClient()
        self.user = UserHttpClient(api_key, api_secret_key)

    def get_coin_summary(self, coin: Ticker) -> CoinSummary:
        time_series_data = self.market.get_valuation(coin.instrument_name, "mark_price")

        df = pd.DataFrame.from_dict(time_series_data)
        df["t"] = df["t"].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
        df["v"] = df["v"].astype(float)

        stats = df
        mean = stats["v"].mean()
        std = stats["v"].std()
        modes = stats["v"].mode()
        percentage_std = float(std) / float(mean)

        return CoinSummary(
            name=coin.instrument_name,
            latest_trade=float(coin.latest_trade),
            mean_24h=mean,
            modes_24h=modes,
            std_24h=std,
            percentage_std_24h=percentage_std,
            percentage_change_24h=float(coin.percentage_change_24h),
            is_greater_than_mean=bool(float(coin.latest_trade) - mean > 0),
            is_greater_than_std=bool(float(coin.latest_trade) - (mean + std) > 0),
        )

    def get_number_of_coins_to_invest_in(self):
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

        number_of_investments = math.floor(total_investable / INVESTMENT_INCREMENTS)

        return total_investable, number_of_investments

    def select_coin(self, strategy) -> CoinSummary:
        coin_summary = None

        for coin in self.market.get_usd_coins():
            logger.info(f"Fetching latest 24hr dataset for {coin.instrument_name}.")

            summary = self.get_coin_summary(coin)

            if CoinSelection.should_select_coin(summary, strategy):
                logger.info(f"Selecting the following coin: {summary}")
                coin_summary = summary
                break
            else:
                logger.info(f"Rejecting the following: {summary}")

        return coin_summary

    def buy_order(
        self,
        instrument_name: str,
        total_price_usd: str,
        latest_trade_price_usd: str,
        tick: str,
        dry_run: bool = True,
    ) -> OrderSummary:
        """Purchase a coin with respect to a total investment amount (e.g I want to purchase 20 dollars worth of Bitcoin)

        Args:
            instrument_name (str): Name of the coin to purchase
            total_price_usd (float): Total cost of the investment (e.g. $20)
            latest_trade_price_usd (float): Price per coin (in USD)
            tick (float): Minimum quantity increment of the coin.
            dry_run (bool, optional): Defaults to True. Set to False to actually purchase coins.

        Returns:
            OrderSummary: _description_
        """

        order_summary = None

        quantity = utils.get_coin_quantity(
            latest_trade_price_usd, total_price_usd, tick
        )

        if not dry_run:
            order = self.user.create_order(
                instrument_name, latest_trade_price_usd, quantity, "BUY"
            )

            order_summary = OrderSummary(
                order.order_id,
                order.client_oid,
                instrument_name,
                latest_trade_price_usd,
                quantity,
            )
        else:
            order_summary = OrderSummary(
                -1,
                str(uuid.uuid4()),
                instrument_name,
                latest_trade_price_usd,
                quantity,
            )

        return order_summary

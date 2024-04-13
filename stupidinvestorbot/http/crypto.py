import logging
import math
import datetime as dt
from typing import List
import uuid
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas import DataFrame

import stupidinvestorbot.utils as utils
from stupidinvestorbot.http.market import MarketHttpClient
from stupidinvestorbot.http.user import UserHttpClient
from stupidinvestorbot.models.app import CoinSummary, OrderSummary, Ticker
from stupidinvestorbot.models.crypto import Order, PositionBalance, UserBalance

INVESTMENT_INCREMENTS = 20.0

logger = logging.getLogger("client")


class CryptoHttpClient:
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

    def get_coin_summaries(self, show_plots=False) -> List[CoinSummary]:
        output = []
        axs = None
        coin_number = 30
        i = 0

        coin_summaries = self.market.get_highest_gain_coins(coin_number)

        if show_plots:
            _, axs = plt.subplots(coin_number)

        for coin in coin_summaries:
            logger.info(f"Fetching latest 24hr dataset for {coin.instrument_name}.")

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

            output.append(CryptoHttpClient.__get_coin_summary(coin, df))

            i += 1

        if show_plots:
            plt.show()

        return output

    def buy_order(
        self,
        instrument_name: str,
        total_price_usd: float,
        latest_trade_price_usd: float,
        tick: float,
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
            response_data = self.user.create_order(
                instrument_name, latest_trade_price_usd, quantity, "BUY"
            )

            order = Order(**response_data)

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

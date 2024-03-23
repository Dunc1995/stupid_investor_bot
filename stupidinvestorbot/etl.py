import json
import pandas as pd
from pandas import DataFrame
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
from stupidinvestorbot import INVESTMENT_INCREMENT
from stupidinvestorbot.crypto import exchange, user
from stupidinvestorbot.models import CoinSummary, PositionBalance, Ticker, UserBalance


def get_investment_increments():
    """
    Get my USD balance and calculate how many coins to invest in.
    """
    balance_dict = json.loads(user.get_balance())["result"]["data"][0]

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

    number_of_investments = math.floor(total_investable / INVESTMENT_INCREMENT)

    return total_investable, number_of_investments


def get_coin_summary(coin: Ticker, valuation: DataFrame) -> CoinSummary:
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


def get_coin_summaries(show_plots=False):
    output = []
    axs = None
    coin_number = 10
    i = 0
    coin_summaries = exchange.get_highest_gain_coins(coin_number)

    if show_plots:
        _, axs = plt.subplots(coin_number)

    for coin in coin_summaries:
        time_series_data = exchange.get_valuation(coin.instrument_name, "mark_price")

        df = pd.DataFrame.from_dict(time_series_data["result"]["data"])
        df["t"] = df["t"].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
        df["v"] = df["v"].astype(float)

        if show_plots:
            axs[i].plot(df["t"], df["v"])
            axs[i].set_title(coin.instrument_name)
            axs[i].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y"))

        output.append(get_coin_summary(coin, df))

        i += 1

    if show_plots:
        plt.show()

    return pd.DataFrame(output)

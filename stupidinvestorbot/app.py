import pandas as pd
from pandas import DataFrame
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import stupidinvestorbot.crypto as crypto
from stupidinvestorbot.models import CoinSummary, Ticker


def __get_summary(coin: Ticker, valuation: DataFrame) -> CoinSummary:
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
    coin_summaries = crypto.get_highest_gain_coins(coin_number)

    if show_plots:
        _, axs = plt.subplots(coin_number)

    for coin in coin_summaries:
        time_series_data = crypto.get_valuation(coin.instrument_name, "mark_price")

        df = pd.DataFrame.from_dict(time_series_data["result"]["data"])
        df["t"] = df["t"].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
        df["v"] = df["v"].astype(float)

        if show_plots:
            axs[i].plot(df["t"], df["v"])
            axs[i].set_title(coin.instrument_name)
            axs[i].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y"))

        output.append(__get_summary(coin, df))

        i += 1

    if show_plots:
        plt.show()

    print(pd.DataFrame(output))


def monitor_coin(instrument_name: str):
    result = crypto.get_instrument_summary(instrument_name)

    print(result)

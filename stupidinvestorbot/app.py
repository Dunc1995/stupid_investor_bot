import json
import pandas as pd
from pandas import DataFrame
import datetime as dt
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import stupidinvestorbot.crypto as crypto
from stupidinvestorbot.models import Ticker


def get_summary(coin : Ticker, valuation : DataFrame) -> dict:
    stats = valuation
    mean = stats['v'].mean()
    std = stats['v'].std()
    percentage_std = float(std) / float(mean)

    return {
        'latest_trade': float(coin.latest_trade),
        'mean_24h': mean,
        'std_24h': std,
        'percentage_std_24h': percentage_std,
        'is_greater_than_mean': bool(float(coin.latest_trade) - mean > 0),
        'is_greater_than_std': bool(float(coin.latest_trade) - (mean + std) > 0) 
        }


def get_time_series_data(show_plots=False):
    axs = None
    coin_number = 10
    i = 0
    coin_summaries = crypto.get_highest_gain_coins(coin_number)

    if show_plots:
        fig, axs = plt.subplots(coin_number)

    for coin in coin_summaries:
        time_series_data = crypto.get_valuation(coin.instrument_name, 'mark_price')

        df = pd.DataFrame.from_dict(time_series_data['result']['data'])
        df['t'] = df['t'].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
        df['v'] = df['v'].astype(float)

        if show_plots:
            axs[i].plot(df['t'], df['v'])
            axs[i].set_title(coin.instrument_name)
            axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))

        with open(os.path.join('output', f'''{coin.instrument_name}.json'''), 'w+') as f:
            f.write(json.dumps(get_summary(coin, df), indent=4))

        i += 1

    if show_plots:
        plt.show()
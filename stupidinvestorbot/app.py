import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import stupidinvestorbot.crypto as crypto


def get_time_series_data():
    coin_number = 10
    i = 0
    coin_summaries = crypto.get_highest_gain_coins(coin_number)

    fig, axs = plt.subplots(coin_number)

    for coin in coin_summaries:
        time_series_data = crypto.get_valuation(coin.instrument_name, 'mark_price')

        df = pd.DataFrame.from_dict(time_series_data['result']['data'])
        df['t'] = df['t'].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
        df['v'] = df['v'].astype(float)

        print(df)

        axs[i].plot(df['t'], df['v'])
        axs[i].set_title(coin.instrument_name)
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))

        i += 1

    plt.show()
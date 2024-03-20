import stupidinvestorbot.crypto as crypto

def get_time_series_data():
    coin_summaries = crypto.get_top_ten_gaining_coins()

    for coin in coin_summaries:
        time_series_data = crypto.get_valuation(coin.instrument_name, 'mark_price')

        with open(f'''{coin.instrument_name.lower()}_time_series.txt''', 'w') as f:
            f.write(time_series_data)
            f.close()

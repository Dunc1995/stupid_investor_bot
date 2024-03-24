from stupidinvestorbot.crypto import exchange
from stupidinvestorbot import etl


def scan_investment_options():
    allocated_coins = []
    total_investable, increments = etl.get_investment_increments()

    coin_summaries_std = list(
        filter(
            lambda summary: not summary.is_greater_than_std, etl.get_coin_summaries()
        )
    )

    coin_summaries_mean = list(
        filter(
            lambda summary: not summary.is_greater_than_mean
            and not summary.is_greater_than_mean,
            coin_summaries_std,
        )
    )

    if len(coin_summaries_std) >= increments:
        while len(allocated_coins) < increments:
            if len(coin_summaries_mean) > 0:
                coin = max(coin_summaries_mean, key=lambda x: x.percentage_std_24h)
                coin_summaries_mean.remove(coin)
                allocated_coins.append(coin)
            elif len(coin_summaries_std) > 0:
                coin = max(coin_summaries_std, key=lambda x: x.percentage_std_24h)
                coin_summaries_std.remove(coin)
                allocated_coins.append(coin)
            else:
                print("Not enough coins")
                break

    print(
        f"""
Investable amount is: ${round(total_investable, 2)}
Number of coins to invest in: {increments}
---
Number of coins within 24h standard deviation: {len(coin_summaries_std)}
Number of coins less than 24h mean: {len(coin_summaries_mean)}

Selected coins: {allocated_coins}
"""
    )


def monitor_coin(instrument_name: str):
    result = exchange.get_instrument_summary(instrument_name)

    print(result)

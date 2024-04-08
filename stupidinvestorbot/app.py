from stupidinvestorbot.crypto import exchange, user
from stupidinvestorbot import INVESTMENT_INCREMENT, etl
from stupidinvestorbot.models import CoinSummary

INSTRUMENT_PROPERTIES = None


def scan_investment_options():
    allocated_coins: list[CoinSummary] = []
    instrument_properties = exchange.get_instrument_properties()
    total_investable, increments = etl.get_investment_increments()

    all_coins = etl.get_coin_summaries()

    sub_coins = [coin for coin in all_coins if coin.name.endswith("_USD")]

    coin_summaries_std = list(
        filter(lambda summary: not summary.is_greater_than_std, sub_coins)
    )

    coin_summaries_mean = list(
        filter(
            lambda summary: not summary.is_greater_than_mean
            and not summary.is_greater_than_mean,
            coin_summaries_std,
        )
    )

    # region Find the most volatile coins
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
    # endregion

    print(
        f"""
Investable amount is: ${round(total_investable, 2)}
Number of coins to invest in: {increments}

Selected coins: {allocated_coins}
"""
    )

    if len(allocated_coins) == increments:
        for coin in allocated_coins:
            coin_props = list(
                filter(lambda x: x.symbol == coin.name, instrument_properties)
            )[
                0
            ]  # TODO there's probably a cleaner way of doing this.

            user.create_order(
                coin.name,
                INVESTMENT_INCREMENT,
                coin.latest_trade,
                coin_props.qty_tick_size,
                "BUY",
            )
            print(f"""Created order for {coin.name}.""")


def monitor_coin(instrument_name: str):
    result = exchange.get_instrument_summary(instrument_name)

    print(result)

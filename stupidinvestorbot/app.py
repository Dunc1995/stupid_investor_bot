import logging
from typing import List
from stupidinvestorbot.models.app import CoinSummary
from stupidinvestorbot.crypto.clients.http.crypto import CryptoHttpClient

logger = logging.getLogger("client")


def select_coins(
    number_of_coins: int, all_coins: List[CoinSummary]
) -> List[CoinSummary]:
    """Basic statistical analysis to determine the most 'desirable' coins to invest in.

    Args:
        number_of_coins (int): The number of coins to invest in based on my wallet balance.
        all_coins (List[CoinSummary]): All coins available on the market.

    Raises:
        IndexError: If not enough coins are found.

    Returns:
        List[CoinSummary]: Coin selection to invest in.
    """
    allocated_coins: List[CoinSummary] = []

    coin_summaries_std = list(
        filter(lambda summary: not summary.is_greater_than_std, all_coins)
    )

    logger.info(f"{len(coin_summaries_std)} coins are within standard deviation.")

    coin_summaries_mean = list(
        filter(
            lambda summary: not summary.is_greater_than_mean,
            coin_summaries_std,
        )
    )

    logger.info(f"{len(coin_summaries_std)} coins are below average market price.")

    if len(coin_summaries_std) >= number_of_coins:
        while len(allocated_coins) < number_of_coins:
            if len(coin_summaries_mean) > 0:
                coin = max(coin_summaries_mean, key=lambda x: x.percentage_std_24h)
                coin_summaries_mean.remove(coin)
                allocated_coins.append(coin)
            elif len(coin_summaries_std) > 0:
                coin = max(coin_summaries_std, key=lambda x: x.percentage_std_24h)
                coin_summaries_std.remove(coin)
                allocated_coins.append(coin)
            else:
                raise IndexError(
                    f"Can't find {number_of_coins} coins to invest in based on the current investment strategy."
                )

    logger.info(f"Number of coins to invest in: {number_of_coins}")
    logger.info(f"Selected coins: {allocated_coins}")

    return allocated_coins


def run(crypto: CryptoHttpClient):
    all_coins = crypto.get_coin_summaries()
    total_investable, number_of_coins = crypto.get_number_of_coins_to_invest_in()

    logger.info(f"Investable amount is: ${round(total_investable, 2)}")

    coin_selection = select_coins(number_of_coins, all_coins)

    # if len(allocated_coins) == increments:
    #     for coin in allocated_coins:
    #         coin_props = list(filter(lambda x: x.symbol == coin.name, instruments))[
    #             0
    #         ]  # TODO there's probably a cleaner way of doing this.

    #         http_client.user.create_order(
    #             coin.name,
    #             40.0,
    #             coin.latest_trade,
    #             coin_props.qty_tick_size,
    #             "BUY",
    #         )
    #         print(f"""Created order for {coin.name}.""")

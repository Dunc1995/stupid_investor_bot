import asyncio
from decimal import Decimal
import logging
from typing import Any, Dict, Generator, List

from crypto_com import MarketClient
from stupidinvestorbot import CRYPTO_KEY, CRYPTO_SECRET_KEY, INVESTMENT_INCREMENTS
from stupidinvestorbot.models.app import CoinSummary, OrderSummary
from stupidinvestorbot.http.crypto import CryptoHttpClient

logger = logging.getLogger("client")
crypto = CryptoHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)

# ! Can probably cash this once db is setup - only wanting the quantity tick size from here
instruments = crypto.market.get_instruments()


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


def purchase_coins(
    coin_selection: List[CoinSummary],
) -> Generator[OrderSummary, Any, None]:
    # TODO this is slow - can probably change this to use the create order list endpoint.
    # ! First coin in the selection is most likely to be successfully purchased.
    for coin in coin_selection:
        coin_props = next(x for x in instruments if x.symbol == coin.name)

        yield crypto.buy_order(
            coin.name,
            INVESTMENT_INCREMENTS,
            coin.latest_trade,
            coin_props.qty_tick_size,
            dry_run=False,
        )


def sell_coin(order: OrderSummary):
    crypto.user.create_order(
        order.coin_name, order.per_coin_price, order.quantity, "SELL"
    )


def get_coin_ticker_data(event: Dict):
    for coin in event["result"]["data"]:
        yield {"name": coin["i"], "price": coin["a"]}


async def monitor_coins_loop(orders: List[OrderSummary]):
    ticker_names = [f"ticker.{order.coin_name}" for order in orders]
    # ena_coin = list(filter(lambda x: x["instrument_name"] == "ENA", balance))[0]

    # instruments = crypto.market.get_instruments()

    # coin_props = list(filter(lambda x: x.symbol == "ENA_USD", instruments))[0]

    async with MarketClient() as client:
        await client.subscribe(ticker_names)
        while True:
            event = await client.next_event()
            if isinstance(event, Dict):
                for coin in get_coin_ticker_data(event):

                    order = next(x for x in orders if x.coin_name == coin["name"])

                    price = coin["price"]

                    percentage_change = Decimal(price) / Decimal(order.per_coin_price)

                    logger.info(
                        f"{coin['name']}    Percentage Change: {round(percentage_change * 100, 2)}%"
                    )

                    if percentage_change > 1.01:
                        order.per_coin_price = price
                        sell_coin(order)
                        logger.info(f"SELLING")


def monitor_coins(orders: List[OrderSummary]):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor_coins_loop(orders))


def run():
    total_investable, number_of_coins = crypto.get_number_of_coins_to_invest_in()

    all_coins = crypto.get_coin_summaries()

    logger.info(f"Investable amount is: ${round(total_investable, 2)}")

    coin_selection = select_coins(number_of_coins, all_coins)

    order_summaries = list(purchase_coins(coin_selection))

    logger.info(order_summaries)

    monitor_coins(order_summaries)

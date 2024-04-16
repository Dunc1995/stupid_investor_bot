import asyncio
from decimal import Decimal
import logging
from typing import Any, Dict, Generator, List

from crypto_com import MarketClient
from stupidinvestorbot import CRYPTO_KEY, CRYPTO_SECRET_KEY, INVESTMENT_INCREMENTS
from stupidinvestorbot.models.app import CoinSummary, OrderSummary, TradingStatus
from stupidinvestorbot.http.crypto import CryptoHttpClient
from stupidinvestorbot.models.crypto import Instrument
import stupidinvestorbot.state as state

logger = logging.getLogger("client")
crypto = CryptoHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)

# ! Can probably cash this once db is setup - only wanting the quantity tick size from here
instruments = crypto.market.get_instruments()


def purchase_coin(coin: CoinSummary, coin_props: Instrument) -> OrderSummary:

    return crypto.buy_order(
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


async def monitor_coins_loop(order: OrderSummary):
    async with MarketClient() as client:
        _coin_name = order.coin_name.replace("_", "-")

        await client.subscribe(
            [f"ticker.{order.coin_name}", f"user.order.{_coin_name}"]
        )

        is_waiting = True

        while is_waiting:
            event = await client.next_event()

            if isinstance(event, Dict) and "result" in event:
                for coin in get_coin_ticker_data(event):
                    price = coin["price"]

                    percentage_change = Decimal(price) / Decimal(order.per_coin_price)

                    logger.info(
                        f"{coin['name']}    Percentage Change: {round(percentage_change * 100, 2)}%"
                    )

                    if percentage_change > 1.005:
                        order.per_coin_price = price
                        sell_coin(order)
                        logger.info(
                            f"Sell order created with the following properties: {order}"
                        )
                        is_waiting = False
            else:
                logger.info(event)


def monitor_coin(order: OrderSummary):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor_coins_loop(order))


def run():
    coin: CoinSummary = None
    instrument: Instrument = None
    order_summary = None
    total_investable, number_of_coins = crypto.get_number_of_coins_to_invest_in()
    logger.info(f"Investable amount is: ${round(total_investable, 2)}")

    for _coin in state.read_existing_trading_statuses():
        order_summary = _coin.order

    if order_summary is None:
        coin = crypto.select_coin()
        instrument = next(x for x in instruments if x.symbol == coin.name)

        coin_data = crypto.market.get_ticker(coin.name)

        latest_trade = Decimal(coin_data.latest_trade)

        percentage_change = latest_trade / Decimal(str(coin.latest_trade))

        if percentage_change > 1.01:
            logger.info(
                f"Skipping purchase of {coin.name} as value has increased since initial analysis."
            )
        else:
            coin.latest_trade = latest_trade

            order_summary = purchase_coin(coin, instrument)

            state.log_trading_status(TradingStatus(order_summary, True, False))

            logger.info(order_summary)

            monitor_coin(order_summary)
    else:
        logger.info(f"Resuming trading session with {order_summary.coin_name}")
        monitor_coin(order_summary)

    run()

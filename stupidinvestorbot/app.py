import asyncio
from decimal import Decimal
import logging
import time
from typing import Dict

from crypto_com import MarketClient, UserClient
from stupidinvestorbot import CRYPTO_KEY, CRYPTO_SECRET_KEY, INVESTMENT_INCREMENTS
from stupidinvestorbot.models.app import CoinSummary, OrderSummary, TradingStatus
from stupidinvestorbot.http.crypto import CryptoHttpClient
from stupidinvestorbot.models.crypto import Instrument
import stupidinvestorbot.state as state

logger = logging.getLogger("client")
crypto = CryptoHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)

# ! Can probably cash this once db is setup - only wanting the quantity tick size from here
instruments = crypto.market.get_instruments()


def monitor_trade(order_id: str):
    logger.info("Order successfully created.")

    order_is_pending = True

    while order_is_pending:
        order_detail = crypto.user.get_order_detail(order_id)

        log_message = "is currently pending."

        if order_detail.successful:
            order_is_pending = False
            log_message = "has been successful."

        logger.info(f"Order {order_id} {log_message}")

        time.sleep(1)


def purchase_coin(coin: CoinSummary, coin_props: Instrument) -> OrderSummary:

    order_summary = crypto.buy_order(
        coin.name,
        INVESTMENT_INCREMENTS,
        coin.latest_trade,
        coin_props.qty_tick_size,
        dry_run=False,
    )

    monitor_trade(order_summary.order_id)

    return order_summary


def sell_coin(order_summary: OrderSummary):
    crypto.user.create_order(
        order_summary.coin_name,
        order_summary.per_coin_price,
        order_summary.quantity,
        "SELL",
    )

    monitor_trade(order_summary.order_id)


def get_coin_ticker_data(event: Dict):
    for coin in event["result"]["data"]:
        yield {"name": coin["i"], "price": coin["a"]}


async def monitor_coins_loop(order: OrderSummary):
    async with MarketClient() as client:
        await client.subscribe([f"ticker.{order.coin_name}"])

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

                    if percentage_change > 1.01:
                        order.per_coin_price = price
                        sell_coin(order)
                        logger.info(
                            f"Sell order created with the following properties: {order}"
                        )
                        state.log_trading_status(
                            TradingStatus(order, True, True, True, True)
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

            state.log_trading_status(
                TradingStatus(order_summary, True, False, False, False)
            )

            logger.info(order_summary)

            monitor_coin(order_summary)
    else:
        logger.info(f"Resuming trading session with {order_summary.coin_name}")
        monitor_coin(order_summary)

    run()

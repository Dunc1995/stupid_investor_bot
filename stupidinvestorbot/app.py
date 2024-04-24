import asyncio
from decimal import Decimal
import logging
import time
from typing import Dict
import numpy as np

from crypto_com import MarketClient
from stupidinvestorbot import CRYPTO_KEY, CRYPTO_SECRET_KEY, INVESTMENT_INCREMENTS
from stupidinvestorbot.models.app import CoinSummary, TradingStatus
from stupidinvestorbot.http.crypto import CryptoHttpClient
from stupidinvestorbot.models.crypto import Instrument
from stupidinvestorbot.strategies import SellPrice
import stupidinvestorbot.utils as utils
import stupidinvestorbot.state as state

logger = logging.getLogger("client")
crypto = CryptoHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)


def order_has_succeeded(order_id: str, number_of_tries: int = 60) -> bool:
    logger.info("Order successfully created.")

    tries = 0
    is_order_successful = False

    while not is_order_successful and tries <= number_of_tries:
        order_detail = crypto.user.get_order_detail(order_id)

        log_message = "is currently pending."

        if order_detail.successful:
            is_order_successful = True
            log_message = "has been successful."

        logger.info(f"Order {order_id} {log_message}")

        time.sleep(2)
        tries += 1

    if not is_order_successful:
        crypto.user.cancel_order(order_id)
        logger.info(f"Order {order_id} was cancelled.")

    return is_order_successful


def purchase_coin(
    coin: CoinSummary, coin_props: Instrument, strategy: str
) -> TradingStatus | None:

    order_summary = crypto.buy_order(
        coin.name,
        INVESTMENT_INCREMENTS,
        coin.latest_trade,
        coin_props.qty_tick_size,
        strategy,
        dry_run=False,
    )

    order_summary.buy_order_created = True
    state.log_trading_status(order_summary)

    _order_has_succeeded = order_has_succeeded(order_summary.order_id)

    order_summary.buy_order_fulfilled = _order_has_succeeded
    state.log_trading_status(order_summary)

    return order_summary if _order_has_succeeded else None


def sell_coin(order_summary: TradingStatus):
    crypto.user.create_order(
        order_summary.coin_name,
        order_summary.per_coin_price,
        order_summary.quantity,
        "SELL",
    )

    order_summary.sell_order_created = True
    state.log_trading_status(order_summary)

    _order_has_succeeded = order_has_succeeded(order_summary.order_id)

    order_summary.sell_order_fulfilled = _order_has_succeeded

    if _order_has_succeeded:
        order_summary.is_running = False

    state.log_trading_status(order_summary)


def get_coin_ticker_data(event: Dict):
    for coin in event["result"]["data"]:
        yield {"name": coin["i"], "price": coin["a"]}


async def monitor_coins_loop(order: TradingStatus):
    async with MarketClient() as client:
        await client.subscribe([f"ticker.{order.coin_name}"])

        percentage_change = None
        is_waiting = True

        while is_waiting:
            event = await client.next_event()

            if isinstance(event, Dict) and "result" in event:
                for coin in get_coin_ticker_data(event):
                    price = coin["price"]

                    _percentage_change = Decimal(price) / Decimal(order.per_coin_price)

                    if _percentage_change != percentage_change:
                        percentage_change = _percentage_change

                        logger.info(
                            f"{coin['name']}    Percentage Change: {round(_percentage_change * 100, 2)}%"
                        )

                    if _percentage_change > SellPrice.get_percentage_increase(order):
                        order.per_coin_price = price
                        sell_coin(order)
                        logger.info(
                            f"Sell order created with the following properties: {order}"
                        )
                        is_waiting = False
            else:
                logger.info(event)


def monitor_coin(order: TradingStatus, qty_tick_size: str):
    coin_balance = crypto.get_coin_balance(order.coin_name)

    order.quantity = utils.correct_coin_quantity(coin_balance.quantity, qty_tick_size)
    logger.info(order)

    try:  # TODO doesn't catch all errors - need better state management
        loop = asyncio.get_event_loop()
        loop.run_until_complete(monitor_coins_loop(order))
    except:
        order.is_running = False
        state.log_trading_status(order)


def run(strategy: str = "high_gain"):
    # ! Can probably cache this once db is setup - only wanting the quantity tick size from here
    instruments = crypto.market.get_instruments()

    order_summary = state.get_resumable_trade()

    if order_summary is None:
        coin = crypto.select_coin(strategy)

        if coin is None:
            logger.info(f"No coins found.")
            run("all_guns_blazing")

        instrument = next(x for x in instruments if x.symbol == coin.name)

        ticker_data = crypto.market.get_ticker(coin.name)
        latest_trade = Decimal(ticker_data.latest_trade)

        percentage_change = latest_trade / Decimal(str(coin.latest_trade))

        if percentage_change > 1.01:
            logger.info(
                f"Skipping purchase of {coin.name} as value has increased since initial analysis."
            )
        else:
            coin.latest_trade = latest_trade

            order_summary = purchase_coin(coin, instrument, strategy)

            # if order_summary is None:
            #     run(strategy)

            if order_summary.buy_order_created:
                monitor_coin(order_summary, instrument.qty_tick_size)
            else:
                logger.info(f"Skipping purchase of {order_summary.coin_name}")
    else:
        logger.info(f"Resuming trading session with {order_summary.coin_name}")

        instrument = next(x for x in instruments if x.symbol == order_summary.coin_name)
        monitor_coin(order_summary, instrument.qty_tick_size)

    # run(strategy)

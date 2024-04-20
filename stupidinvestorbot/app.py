import asyncio
from decimal import Decimal
import logging
import time
from typing import Dict

from crypto_com import MarketClient
from stupidinvestorbot import CRYPTO_KEY, CRYPTO_SECRET_KEY, INVESTMENT_INCREMENTS
from stupidinvestorbot.models.app import CoinSummary, TradingStatus
from stupidinvestorbot.http.crypto import CryptoHttpClient
from stupidinvestorbot.models.crypto import Instrument
import stupidinvestorbot.utils as utils
import stupidinvestorbot.state as state

logger = logging.getLogger("client")
crypto = CryptoHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)


def order_has_succeeded(order_id: str) -> bool:
    logger.info("Order successfully created.")

    tries = 0
    is_order_successful = False

    while not is_order_successful and tries <= 60:
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


def purchase_coin(coin: CoinSummary, coin_props: Instrument) -> TradingStatus:

    order_summary = crypto.buy_order(
        coin.name,
        INVESTMENT_INCREMENTS,
        coin.latest_trade,
        coin_props.qty_tick_size,
        dry_run=False,
    )

    order_summary.buy_order_created = True
    state.log_trading_status(order_summary)

    order_summary.buy_order_fulfilled = order_has_succeeded(order_summary.order_id)
    state.log_trading_status(order_summary)

    return order_summary


def sell_coin(order_summary: TradingStatus):
    crypto.user.create_order(
        order_summary.coin_name,
        order_summary.per_coin_price,
        order_summary.quantity,
        "SELL",
    )

    order_summary.sell_order_created = True
    state.log_trading_status(order_summary)

    order_summary.sell_order_fulfilled = order_has_succeeded(order_summary.order_id)
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

                    if _percentage_change > 1.01:
                        order.per_coin_price = price
                        sell_coin(order)
                        logger.info(
                            f"Sell order created with the following properties: {order}"
                        )
                        is_waiting = False
            else:
                logger.info(event)


def monitor_coin(order: TradingStatus):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor_coins_loop(order))


def run(strategy: str = "high_gain"):
    # ! Can probably cache this once db is setup - only wanting the quantity tick size from here
    instruments = crypto.market.get_instruments()

    order_summary = state.get_resumable_trade()

    if order_summary is None:
        coin = crypto.select_coin(strategy)
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

            order_summary = purchase_coin(coin, instrument)
            coin_balance = crypto.get_coin_balance(coin.name)

            order_summary.quantity = utils.correct_coin_quantity(
                coin_balance.quantity, instrument.qty_tick_size
            )

            if order_summary.buy_order_created:
                logger.info(order_summary)

                monitor_coin(order_summary)
            else:
                logger.info(f"Skipping purchase of {order_summary.coin_name}")
    else:
        logger.info(f"Resuming trading session with {order_summary.coin_name}")
        monitor_coin(order_summary)

    run()

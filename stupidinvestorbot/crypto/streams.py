import json
from typing import Dict
from crypto_com import MarketClient, UserClient
import asyncio
import os
import logging
from stupidinvestorbot.crypto import CRYPTO_KEY, CRYPTO_SECRET_KEY, exchange, user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")


# ! Buggy as fuck
async def run():
    balance = json.loads(user.get_balance())["result"]["data"][0]["position_balances"]

    ena_coin = list(filter(lambda x: x["instrument_name"] == "ENA", balance))[0]

    print(balance)

    instrument_properties = exchange.get_instrument_properties()

    coin_props = list(filter(lambda x: x.symbol == "ENA_USD", instrument_properties))[0]

    async with MarketClient() as client:
        await client.subscribe(["ticker.ENA_USD"])
        while True:
            event = await client.next_event()
            if isinstance(event, Dict):
                latest_trade = float(event["result"]["data"][0]["a"])
                coin_value = 1.15911  # Need to grab this from order history

                percentage_value = latest_trade / coin_value

                if percentage_value > 1.0:
                    print(latest_trade)
                    print(f"{percentage_value * 100}%")
                    if percentage_value > 1.01:
                        print("SELLLINGGGG")

                        print(coin_props.qty_tick_size)

                        user.create_order(
                            "ENA_USD",
                            float(coin_props.qty_tick_size) * latest_trade,
                            latest_trade,
                            coin_props.qty_tick_size,
                            "SELL",
                        )

                        break
                else:
                    print("Coin's doing shite")


def orders():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

from typing import Dict
from crypto_com import MarketClient
import asyncio
import logging

from stupidinvestorbot.crypto.clients import HttpClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")


# ! Buggy as fuck
async def run(http_client: HttpClient):
    balance = http_client.user.get_balance()[0][
        "position_balances"
    ]  # ! zero index refers to master wallet

    ena_coin = list(filter(lambda x: x["instrument_name"] == "ENA", balance))[0]

    print(balance)

    instruments = http_client.market.get_instruments()

    coin_props = list(filter(lambda x: x.symbol == "ENA_USD", instruments))[0]

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

                        http_client.user.create_order(
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

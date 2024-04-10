import json
from typing import Dict
from stupidinvestorbot import quantities
from stupidinvestorbot.crypto.clients.http.base import AuthenticatedHttpClient


class UserHttpClient(AuthenticatedHttpClient):
    def __init__(
        self,
        api_key,
        api_secret_key,
        api_url="https://api.crypto.com/exchange/v1/private/",
    ):
        super().__init__(
            api_key=api_key, api_secret_key=api_secret_key, api_url=api_url
        )

    def get_balance(self) -> Dict:
        return self.post_request(1, "user-balance")[
            0
        ]  # ! zero index assumes only one wallet - may break

    # ! TODO Streamline this
    def create_order(
        self,
        instrument_name: str,
        investment_total_usd: float,
        instrument_price_usd: float,
        quantity_tick: float,
        side: str,
    ):
        global buy_order_id
        print("Quantity increment is: " + quantity_tick)

        # TODO this needs fixing/testing - not foolproof
        quantity = quantities.get_coin_quantity(
            instrument_price_usd, investment_total_usd, quantity_tick
        )

        print(f"Total quantity is: {quantity}")
        print(f"Estimate order price (USD): {quantity*instrument_price_usd}")

        params = {
            "instrument_name": instrument_name,
            "side": side,
            "type": "LIMIT",
            "price": f"{instrument_price_usd}",
            "quantity": f"{quantity}",
            "time_in_force": "GOOD_TILL_CANCEL",
        }

        print(json.dumps(params, indent=4))

        result = self.post_request(buy_order_id, "create-order", params)

        buy_order_id += 1

        return result

    def get_open_orders(self, instrument_name=None):
        args = {} if instrument_name is None else {"instrument_name": instrument_name}

        return self.post_request(4, "get-open-orders", args)

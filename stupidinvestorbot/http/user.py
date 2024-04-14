from decimal import Decimal
import json
from typing import Dict
from stupidinvestorbot import utils
from stupidinvestorbot.http.base import AuthenticatedHttpClient


class UserHttpClient(AuthenticatedHttpClient):
    def __init__(
        self,
        api_key,
        api_secret_key,
        api_url="https://api.crypto.com/exchange/v1/private/",
    ):
        super().__init__(
            id_incr=1, api_key=api_key, api_secret_key=api_secret_key, api_url=api_url
        )

    def get_balance(self) -> Dict:
        return self.post_request("user-balance")[
            0
        ]  # ! zero index assumes only one wallet - may break

    def create_order(
        self,
        instrument_name: str,
        instrument_price_usd: str,
        quantity: str,
        side: str,
    ) -> Dict:
        """Creates a buy or sell order for a specific coin. Quantity has to be a multiple of the coin's
        quantity tick size.

        Args:
            instrument_name (str): Name of the crypto coin.
            instrument_price_usd (float): Specific crypto coin price.
            quantity (str): Number of coins to buy or sell.
            side (str): BUY or SELL.

        Returns:
            Dict: response from the buy or sell order.
        """

        params = {
            "instrument_name": instrument_name,
            "side": side,
            "type": "LIMIT",
            "price": f"{instrument_price_usd}",
            "quantity": f"{quantity}",
            "time_in_force": "GOOD_TILL_CANCEL",
        }

        result = self.post_request("create-order", params)

        return result

    def get_open_orders(self, instrument_name=None):
        args = {} if instrument_name is None else {"instrument_name": instrument_name}

        return self.post_request("get-open-orders", args)

from stupidinvestorbot.crypto import auth
import math


def get_balance() -> str:
    return auth.post_request(1, "user-balance")


def buy_order(
    instrument_name: str, price: float, market_price: float, traded_volume_24h: float
):

    _market_price = float(market_price)
    quantity = float(price) / _market_price

    divisor = "1"
    remainder = 0.0
    while remainder == 0.0:  # TODO - needs fixing. can shit the bed quite easily.
        remainder = float(traded_volume_24h) % float(divisor)

        if remainder == 0.0:
            divisor = divisor + "0"

    print("Quantity increment is: " + divisor)

    increments = math.floor(quantity / float(divisor))
    quantity = f"{increments * float(divisor)}"

    params = {
        "instrument_name": instrument_name,
        "side": "BUY",
        "type": "LIMIT",
        "price": f"{_market_price:.10f}",
        "quantity": quantity,
        "time_in_force": "GOOD_TILL_CANCEL",
    }

    return auth.post_request(2, "create-order", params)


# def cancel_order():


def get_open_orders(instrument_name=None):
    args = {} if instrument_name is None else {"instrument_name": instrument_name}

    return auth.post_request(4, "get-open-orders", args)


# def get_order_details():

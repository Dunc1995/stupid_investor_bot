from stupidinvestorbot.crypto import auth
import math
import json


buy_order_id = 1


def __correct_amount_via_tick_size(amount: float, tick: float) -> float:
    """
    Precise amounts can cause the Crypto API to complain -
    this corrects the amount using the input tick value.
    """

    _amount = float(amount)
    _tick = float(tick)

    remainder = _amount % _tick

    return _amount - remainder


def __get_coin_quantity(
    instrument_price_usd: float, investment_total_usd: float, tick: float
) -> float:
    _instrument_price_usd = float(instrument_price_usd)

    absolute_quantity = float(investment_total_usd) / _instrument_price_usd

    return __correct_amount_via_tick_size(absolute_quantity, tick)


def get_balance() -> str:
    return auth.post_request(1, "user-balance")


def buy_order(
    instrument_name: str,
    investment_total_usd: float,
    instrument_price_usd: float,
    quantity_tick: float,
):
    global buy_order_id
    print("Quantity increment is: " + quantity_tick)

    quantity = __get_coin_quantity(
        instrument_price_usd, investment_total_usd, quantity_tick
    )

    print(f"Total quantity is: {quantity}")
    print(f"Estimate order price (USD): {quantity*instrument_price_usd}")

    params = {
        "instrument_name": instrument_name,
        "side": "BUY",
        "type": "LIMIT",
        "price": f"{instrument_price_usd}",
        "quantity": f"{quantity}",
        "time_in_force": "GOOD_TILL_CANCEL",
    }

    print(json.dumps(params, indent=4))

    result = auth.post_request(buy_order_id, "create-order", params)

    buy_order_id += 1

    return result


# def cancel_order():


def get_open_orders(instrument_name=None):
    args = {} if instrument_name is None else {"instrument_name": instrument_name}

    return auth.post_request(4, "get-open-orders", args)


# def get_order_details():

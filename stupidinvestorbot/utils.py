from decimal import *


def __correct_amount_via_tick_size(amount: str, tick: str) -> Decimal:
    """
    Precise amounts can cause the Crypto API to complain -
    this corrects the amount using the input tick value.
    """

    _amount = Decimal(amount)
    _tick = Decimal(tick)

    remainder = _amount % _tick

    return _amount - remainder


def get_coin_quantity(
    instrument_price_usd: str, investment_total_usd: str, tick: str
) -> Decimal:
    _instrument_price_usd = Decimal(instrument_price_usd)

    absolute_quantity = Decimal(investment_total_usd) / _instrument_price_usd

    return __correct_amount_via_tick_size(absolute_quantity, tick)

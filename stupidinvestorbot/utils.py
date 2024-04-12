def __correct_amount_via_tick_size(amount: float, tick: float) -> float:
    """
    Precise amounts can cause the Crypto API to complain -
    this corrects the amount using the input tick value.
    """

    _amount = float(amount)
    _tick = float(tick)

    remainder = _amount % _tick

    return _amount - remainder


def get_coin_quantity(
    instrument_price_usd: float, investment_total_usd: float, tick: float
) -> float:
    _instrument_price_usd = float(instrument_price_usd)

    absolute_quantity = float(investment_total_usd) / _instrument_price_usd

    return __correct_amount_via_tick_size(absolute_quantity, tick)

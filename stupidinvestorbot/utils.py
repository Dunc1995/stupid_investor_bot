from decimal import *
import logging


logger = logging.getLogger("client")


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


def non_essential(func):
    """Decorator for suppressing errors from non-integral code. Don't go mental with this
    decorator.
    """

    def inner(*args, **kwargs):
        try:
            return func(**args, **kwargs)
        except:
            logger.warn(
                f"Code has failed for {str(func)}. This error has been suppressed so trading can continue."
            )

        return None

    return inner

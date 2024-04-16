from dataclasses import dataclass
import time

from pandas import Series
from stupidinvestorbot.models.crypto import Order


@dataclass
class Ticker:
    """Maps abbreviated property names from public/get-tickers query to human readable properties."""

    instrument_name: str
    highest_trade_24h: str
    lowest_trade_24h: str
    latest_trade: str
    total_traded_volume_24h: str
    total_traded_volume_usd_24h: str
    percentage_change_24h: str
    best_bid_price: str
    best_ask_price: str
    open_interest: str
    timestamp: int

    def __init__(self, obj):
        self.instrument_name = obj["i"]
        self.highest_trade_24h = obj["h"]
        self.lowest_trade_24h = obj["l"]
        self.latest_trade = obj["a"]
        self.total_traded_volume_24h = obj["v"]
        self.total_traded_volume_usd_24h = obj["vv"]
        self.percentage_change_24h = obj["c"]
        self.best_bid_price = obj["b"]
        self.best_ask_price = obj["k"]
        self.open_interest = obj["oi"]
        self.timestamp = obj["t"]


@dataclass
class CoinSummary:
    """Data container for storing basic statistical properties after
    analyzing valuation data for a particular coin.
    """

    name: str
    latest_trade: float
    mean_24h: float
    modes_24h: Series
    std_24h: float
    percentage_change_24h: float
    percentage_std_24h: float
    is_greater_than_mean: bool
    is_greater_than_std: bool

    @property
    def has_few_modes(self) -> bool:
        """Potentially useful if a low number of modes signifies a fairly stable coin resembling
        "white noise" variability.

        Returns:
            bool: True if low number of modes for the given dataset.
        """
        return len(self.modes_24h) < 5

    @property
    def has_high_std(self) -> bool:
        """Useful to work out which coins are the most volatile at any point in time.

        Returns:
            bool: True if standard deviation is higher than the given threshold.
        """
        return self.percentage_std_24h > 0.03

    @property
    def has_low_change(self) -> bool:
        """I'm assuming it's a safe assumption that a volatile coin at its mean or lower than average
        will hopefully have a rebound back to a value above its mean. Use this property to invest at the
        average price or lower.

        Returns:
            bool: True if percentage change is close to zero.
        """
        return self.percentage_change_24h < 0.01 and self.percentage_change_24h > -0.02


@dataclass
class OrderSummary(Order):
    coin_name: str
    per_coin_price: float
    quantity: float

    @property
    def total_usd(self):
        return float(self.quantity) * float(self.per_coin_price)


@dataclass
class TradingStatus:
    order: OrderSummary
    order_created: bool
    order_fulfilled: bool
    __timestamp: int = None

    @property
    def timestamp(self) -> int:
        if self.__timestamp is None:
            self.__timestamp = int(time.time())

        return self.__timestamp

    @timestamp.setter
    def timestamp(self, stamp: int):
        stamp = self.__timestamp

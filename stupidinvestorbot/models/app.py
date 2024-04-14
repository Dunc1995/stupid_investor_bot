from dataclasses import dataclass

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
    modal_24h: float
    std_24h: float
    percentage_std_24h: float
    is_greater_than_mean: bool
    is_greater_than_std: bool


@dataclass
class OrderSummary(Order):
    coin_name: str
    per_coin_price: float
    quantity: float

    @property
    def total_usd(self):
        return float(self.quantity) * float(self.per_coin_price)

from dataclasses import dataclass

@dataclass
class Ticker():
    instrument_name : str
    highest_trade_24h : str
    lowest_trade_24h : str
    latest_trade : str
    total_traded_volume_24h : str
    total_traded_volume_usd_24h  : str
    percentage_change_24h : str
    best_bid_price : str
    best_ask_price : str
    open_interest  : str
    timestamp : int

    def __init__(self, obj):
        self.instrument_name = obj['i']
        self.highest_trade_24h = obj['h']
        self.lowest_trade_24h = obj['l']
        self.latest_trade = obj['a']
        self.total_traded_volume_24h = obj['v']
        self.total_traded_volume_usd_24h = obj['vv']
        self.percentage_change_24h = obj['c']
        self.best_bid_price = obj['b']
        self.best_ask_price = obj['k']
        self.open_interest = obj['oi']
        self.timestamp = obj['t']

from dataclasses import dataclass


@dataclass
class PositionBalance:
    instrument_name: str
    quantity: float
    market_value: float
    collateral_eligible: bool
    haircut: float
    collateral_amount: float
    max_withdrawal_balance: float
    reserved_qty: float
    hourly_interest_rate: float


@dataclass
class UserBalance:
    total_available_balance: float
    total_margin_balance: float
    total_initial_margin: float
    total_position_im: float
    total_haircut: float
    total_maintenance_margin: float
    total_position_cost: float
    total_cash_balance: float
    total_collateral_value: float
    total_session_unrealized_pnl: float
    instrument_name: str
    total_session_realized_pnl: float
    is_liquidating: bool
    credit_limits: list
    total_effective_leverage: float
    total_borrow: float
    position_limit: float
    used_position_limit: float
    position_balances: list[PositionBalance]
    has_risk: bool
    terminatable: bool
    margin_score: float


@dataclass
class Ticker:
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
    name: str
    latest_trade: float
    mean_24h: float
    std_24h: float
    percentage_std_24h: float
    is_greater_than_mean: bool
    is_greater_than_std: bool


@dataclass
class Instrument:
    symbol: str
    inst_type: str
    display_name: str
    base_ccy: str
    quote_ccy: str
    quote_decimals: int
    quantity_decimals: int
    price_tick_size: str
    qty_tick_size: str
    max_leverage: str
    tradable: str
    expiry_timestamp_ms: int
    beta_product: bool
    margin_buy_enabled: bool
    margin_sell_enabled: bool
    contract_size: str = None
    underlying_symbol: str = None

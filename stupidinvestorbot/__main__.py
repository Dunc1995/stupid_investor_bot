import argh
from stupidinvestorbot.crypto import user, exchange
from stupidinvestorbot import etl
import stupidinvestorbot.app as app

if __name__ == "__main__":
    argh.dispatch_commands(
        [
            user.get_open_orders,
            user.get_balance,
            exchange.get_instrument_properties,
            etl.get_coin_summaries,
            etl.get_investment_increments,
            app.monitor_coin,
            app.scan_investment_options,
        ]
    )

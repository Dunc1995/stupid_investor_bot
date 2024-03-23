from stupidinvestorbot.crypto import exchange
from stupidinvestorbot import etl


def scan_investment_options():
    total_investable, increments = etl.get_investment_increments()

    print(
        f"""
Investable amount is: ${round(total_investable, 2)}
Number of coins to invest in: {increments}
"""
    )


def monitor_coin(instrument_name: str):
    result = exchange.get_instrument_summary(instrument_name)

    print(result)

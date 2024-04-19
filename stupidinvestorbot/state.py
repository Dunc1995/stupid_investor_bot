import simplejson as json
import logging
import os
import time
from typing import Any, Generator, List

from stupidinvestorbot.models.app import OrderSummary, TradingStatus

# TODO use abspath
TRADES_PATH = "./trades"
logger = logging.getLogger("client")


def create_directory():
    if not os.path.exists(TRADES_PATH):
        os.makedirs(TRADES_PATH)
        logger.info("Creating trades directory.")


def log_trading_status(status: TradingStatus):
    create_directory()

    with open(
        os.path.join(
            TRADES_PATH, f"{status.order.coin_name.lower()}_{status.timestamp}.json"
        ),
        "w+",
    ) as f:
        summary_dict = status.order.__dict__
        status_dict = status.__dict__
        status_dict["order"] = summary_dict

        data_string = json.dumps(status_dict, indent=4, use_decimal=True)

        f.write(data_string)


def read_existing_trading_statuses() -> Generator[TradingStatus, Any, None]:
    create_directory()

    for file_name in os.listdir(TRADES_PATH):
        status = None

        with open(os.path.join(TRADES_PATH, file_name), "r") as f:
            status_dict = json.loads(f.read())
            status_dict["order"] = OrderSummary(**status_dict["order"])

            status = TradingStatus(**status_dict)

        if not status.buy_order_fulfilled:
            yield status

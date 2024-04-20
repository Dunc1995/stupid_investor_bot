import simplejson as json
import logging
import os
import time
from typing import Any, Generator

from stupidinvestorbot.models.app import TradingStatus

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
        status_dict = status.__dict__

        data_string = json.dumps(status_dict, indent=4, use_decimal=True)

        f.write(data_string)


def get_resumable_trade() -> TradingStatus | None:
    status = None
    create_directory()

    for file_name in os.listdir(TRADES_PATH):

        with open(os.path.join(TRADES_PATH, file_name), "r") as f:
            status_dict = json.loads(f.read())
            status = TradingStatus(**status_dict)

        if status.is_resumable and not status.is_running:
            status.is_running = True
            log_trading_status(status)
            break
        else:
            status = None  # important to set to None here to prevent code trying to execute on completed trades.

    return status

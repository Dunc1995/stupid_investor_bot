import logging
import argh
from stupidinvestorbot import app as app

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    argh.dispatch_command(app.run)

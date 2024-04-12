import logging
import argh
from stupidinvestorbot import app as app

logging.basicConfig(level=logging.INFO)


def main():
    app.run()


if __name__ == "__main__":
    argh.dispatch_commands([main])

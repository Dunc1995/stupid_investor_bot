import logging
import os
import argh
from stupidinvestorbot.crypto.clients.http.crypto import CryptoHttpClient
from stupidinvestorbot import app as app

# Prefixed with CRYPTO incase additional API's are added.
CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")

logging.basicConfig(level=logging.INFO)

crypto = CryptoHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)


def main():
    app.run(crypto)


if __name__ == "__main__":
    argh.dispatch_commands([main])

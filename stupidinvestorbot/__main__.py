import os
import argh
from stupidinvestorbot.crypto import clients
from stupidinvestorbot import app as app

# Prefixed with CRYPTO incase additional API's are added.
CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")
http_client = clients.HttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)


def main():
    app.run(http_client)


if __name__ == "__main__":
    argh.dispatch_commands([main])

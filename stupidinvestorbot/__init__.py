import os

# Prefixed with CRYPTO incase additional API's are added.
CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")
CRYPTO_REST_API = "https://api.crypto.com/exchange/v1"

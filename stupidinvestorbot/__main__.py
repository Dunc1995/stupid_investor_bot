import json
from stupidinvestorbot import REST_API
from stupidinvestorbot.credentials import read_api_credentials
from stupidinvestorbot.crypto import CryptoClient

if __name__ == "__main__":
    credentials = read_api_credentials()
    client = CryptoClient(REST_API, credentials)

    print(json.dumps(client.get_volatile_coins(), indent=4))

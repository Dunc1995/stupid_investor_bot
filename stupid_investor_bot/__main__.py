from stupid_investor_bot import REST_API
from stupid_investor_bot.credentials import read_api_credentials
from stupid_investor_bot.crypto import CryptoClient

if __name__ == "__main__":
    credentials = read_api_credentials()
    client = CryptoClient(REST_API, credentials)

    print(client.show_balance())

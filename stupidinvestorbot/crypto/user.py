from stupidinvestorbot.crypto import auth


def get_balance() -> str:
    return auth.post_request(1, "user-balance")


# def create_order():

# def cancel_order():


def get_open_orders(instrument_name=None):
    args = {} if instrument_name is None else {"instrument_name": instrument_name}

    return auth.post_request(4, "get-open-orders", args)


# def get_order_details():

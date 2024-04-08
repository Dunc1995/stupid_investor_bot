import hashlib
import json
import time
import requests
import hmac
from stupidinvestorbot.crypto import CRYPTO_REST_API, CRYPTO_KEY, CRYPTO_SECRET_KEY

MAX_LEVEL = 3


def __params_to_str(obj, level):
    if level >= MAX_LEVEL:
        return str(obj)

    return_str = ""
    for key in sorted(obj):
        return_str += key
        if obj[key] is None:
            return_str += "null"
        elif isinstance(obj[key], list):
            for subObj in obj[key]:
                return_str += __params_to_str(subObj, level + 1)
        else:
            return_str += str(obj[key])
    return return_str


def __get_signature(req: dict) -> str:
    """
    See https://exchange-docs.crypto.com/exchange/v1/rest-ws/index.html#digital-signature
    """

    # First ensure the params are alphabetically sorted by key
    param_str = ""

    if "params" in req:
        param_str = __params_to_str(req["params"], 0)

    payload_str = (
        req["method"] + str(req["id"]) + req["api_key"] + param_str + str(req["nonce"])
    )

    return hmac.new(
        bytes(str(CRYPTO_SECRET_KEY), "utf-8"),
        msg=bytes(payload_str, "utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def post_request(id: int, method: str, params={}) -> str:
    req = {
        "id": id,
        "method": "private/" + method,
        "api_key": CRYPTO_KEY,
        "params": params,
        "nonce": int(time.time() * 1000),
    }

    print("I got here with: " + json.dumps(req, indent=4))

    req["sig"] = __get_signature(req)

    headers = {"Content-Type": "application/json"}

    result = requests.post(
        f"""{CRYPTO_REST_API}/private/{method}""", json=req, headers=headers
    )

    if result.status_code != 200:
        raise ValueError(result.text)

    return result.text


def get_websocket_authorization_data() -> dict:
    req = {
        "id": 1,
        "method": "public/auth",
        "api_key": CRYPTO_KEY,
        "nonce": int(time.time() * 1000),
    }

    req["sig"] = __get_signature(req)

    return req

import hashlib
import time
import requests
import hmac
from stupidinvestorbot import CRYPTO_REST_API, CRYPTO_KEY, CRYPTO_SECRET_KEY

MAX_LEVEL = 3


def params_to_str(obj, level):
    if level >= MAX_LEVEL:
        return str(obj)

    return_str = ""
    for key in sorted(obj):
        return_str += key
        if obj[key] is None:
            return_str += "null"
        elif isinstance(obj[key], list):
            for subObj in obj[key]:
                return_str += params_to_str(subObj, level + 1)
        else:
            return_str += str(obj[key])
    return return_str


def get_signature(req: dict) -> str:
    # First ensure the params are alphabetically sorted by key
    param_str = ""

    if "params" in req:
        param_str = params_to_str(req["params"], 0)

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
        "method": method,
        "api_key": CRYPTO_KEY,
        "params": params,
        "nonce": int(time.time() * 1000),
    }

    req["sig"] = get_signature(req)

    headers = {"Content-Type": "application/json"}

    result = requests.post(
        f"""{CRYPTO_REST_API}/private/{method}""", json=req, headers=headers
    )

    return result.text

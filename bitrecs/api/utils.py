import os
import json
import bittensor as bt
import traceback
import requests

from typing import Any, Dict, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse


def is_api_data_valid(data) -> tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "Not a dictionary"

    if "keys" not in data.keys():
        return False, "Missing users key"

    if not isinstance(data["keys"], dict):
        return False, "Keys field is not a dict"

    for key, value in data["keys"].items():
        if not isinstance(value, dict):
            return False, "Key value is not a dictionary"
        if "requests_per_min" not in value.keys():
            return False, "Missing requests_per_min field"
        if not isinstance(value["requests_per_min"], int):
            return False, "requests_per_min is not an int"

    return True, "Formatting is good"


def load_api_config() -> Optional[dict]:
    bt.logging.trace("Loading API config")
    try:
        if not os.path.exists("template/api/api.json"):
            raise Exception(f"{'template/api/api.json'} does not exist")

        with open("template/api/api.json", 'r') as file:
            api_data = json.load(file)
            #bt.logging.trace("api_data", api_data)
            valid, reason = is_api_data_valid(api_data)
            if not valid:
                raise Exception(f"{'api/api.json'} is poorly formatted. {reason}")
            if "change-me" in api_data["keys"]:
                bt.logging.error("YOU ARE USING THE DEFAULT API KEY. CHANGE IT FOR SECURITY REASONS.")
        return api_data
    except Exception as e:
        bt.logging.error("Error loading API config:", e)
        traceback.print_exc()


def _get_api_key(request: Request) -> Any:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return auth_header


async def api_key_validator(request, call_next) -> Response:
    if request.url.path in ["/favicon.ico"]:
        return await call_next(request)

    api_key = _get_api_key(request)
    if not api_key:
        bt.logging.error(f"ERROR - Request has no Authorization {request.client.host}")
        return JSONResponse(status_code=400, content={"detail": "Authorization is missing"})

    api_key_info = load_api_config()
    if api_key_info is None:
        bt.logging.error(f"ERROR - MISSING API request key {request.client.host}")
        return JSONResponse(status_code=401, content={"detail": "Invalid API key config"})
    
    if api_key not in api_key_info["keys"]:
        bt.logging.error(f"ERROR - INVALID API request key {request.client.host}")        
        return JSONResponse(status_code=401, content={"detail": "Invalid API key request"})

    response: Response = await call_next(request)
    return response


async def check_validator_status(ip, port, timeout=3) -> bool:
    try:
        api_key_info = load_api_config()
        if api_key_info is None or "keys" not in api_key_info:
            bt.logging.error(f"ERROR - MISSING API request key")
            return False
        key = str(next(iter(api_key_info["keys"])))
        url = f"http://{ip}:{port}/ping"
        headers = {"Authorization": f"Bearer {key}"}
        r = requests.get(url, headers=headers, timeout=timeout)
        return r.status_code == 200
    except Exception as e:
        bt.logging.error(f"Error checking server status: {e}")
        return False
import os
import json
import bittensor as bt
import traceback
import httpx
import requests

from typing import Any, Dict, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


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
        if not os.path.exists("bitrecs/api/api.json"):
            raise Exception(f"{'bitrecs/api/api.json'} does not exist")

        with open("bitrecs/api/api.json", 'r') as file:
            api_data = json.load(file)            
            valid, reason = is_api_data_valid(api_data)
            if not valid:
                raise Exception(f"{'api/api.json'} is poorly formatted. {reason}")
            if "change-me" in api_data["keys"]:
                bt.logging.error("\033[33m YOU ARE USING THE DEFAULT API KEY. CHANGE IT FOR SECURITY REASONS. \033[0m")
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


async def api_key_validator(self, request, call_next) -> Response:
    if request.url.path in ["/favicon.ico"]:
        return await call_next(request)

    api_key = _get_api_key(request)
    if not api_key:
        bt.logging.error(f"ERROR - Request has no Authorization {request.client.host}")
        return JSONResponse(status_code=400, content={"detail": "Authorization is missing"})

    # api_key_info = load_api_config()
    # if api_key_info is None:
    #     bt.logging.error(f"ERROR - MISSING API request key {request.client.host}")
    #     return JSONResponse(status_code=401, content={"detail": "Invalid API key config"})
    
    # if api_key not in api_key_info["keys"]:
    #     bt.logging.error(f"ERROR - INVALID API request key {request.client.host}")        
    #     return JSONResponse(status_code=401, content={"detail": "Invalid API key request"})
    
    bitrecs_api_key = self.bitrecs_api_key
    if not bitrecs_api_key:
        bt.logging.error(f"ERROR - MISSING BITRECS_API_KEY")
        return JSONResponse(status_code=500, content={"detail": "Server error - invalid API key"})
    if api_key != bitrecs_api_key:
        bt.logging.error(f"ERROR - INVALID API request key mismatch {request.client.host}")        
        return JSONResponse(status_code=401, content={"detail": "Invalid API key request"})
    
    #TODO: this gets called even after a RateLimitExeption has been raised
    try:
        response: Response = await call_next(request)
        return response
    except Exception as e:
        bt.logging.error(f"ERROR api_key_validator - {e}")
        return JSONResponse(status_code=500, 
                            content={"detail": "Internal server error - key validator"})
    
    

def get_proxy_public_key(proxy_url: str) -> bytes:
    with httpx.Client(timeout=httpx.Timeout(15)) as client:
        response = client.get(
            f"{proxy_url}/public_key",
        )
    response.raise_for_status()
    pub_key = response.json()["public_key"]
    raw_bytes = bytes.fromhex(pub_key)
    return raw_bytes
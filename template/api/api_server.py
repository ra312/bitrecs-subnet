import os
import json
import time
import uvicorn
import traceback
import bittensor as bt
from typing import Callable, Awaitable, List, Optional, Any
from fastapi import FastAPI, Request, APIRouter, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from bittensor.core.axon import FastAPIThreadedServer
from template.protocol import BitrecsRequest

ForwardFn = Callable[[BitrecsRequest], BitrecsRequest]

auth_data = dict()
request_counts = {}


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
        return JSONResponse(
            status_code=400,
            content={"detail": "API key is missing"}
        )

    api_key_info = load_api_config()
    if api_key_info is None:
        return JSONResponse(status_code=401, content={"detail": "Invalid API key config"})
    
    if api_key not in api_key_info["keys"]:
        return JSONResponse(status_code=401, content={"detail": "Invalid API key request"})

    response: Response = await call_next(request)
    return response




class ApiServer:
    app: FastAPI
    fast_server: FastAPIThreadedServer
    router: APIRouter
    forward_fn: ForwardFn  

    def __init__(self, axon_port: int, forward_fn: ForwardFn, api_json: str):
        self.forward_fn = forward_fn
        self.app = FastAPI()        
        self.app.middleware('http')(api_key_validator)
        self.app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=5)
        #self.app.middleware('http')(auth_rate_limiting_middleware)

        self.fast_server = FastAPIThreadedServer(config=uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=axon_port,
            log_level="trace" if bt.logging.__trace_on__ else "critical"
        ))

        self.router = APIRouter()
        self.router.add_api_route(
            "/ping", 
            self.ping,            
            methods=["GET"],
        )
        self.router.add_api_route(
            "/rec", 
            self.get_rec,            
            methods=["POST"]  
        )
       
        self.app.include_router(self.router)
        self.api_json = api_json

        self.tunnel = None
        bt.logging.info(f"\033[1;32m API Server initialized \033[0m")

    async def ping(self):
        bt.logging.info(f"\033[1;32m API Server ping \033[0m")
        return JSONResponse(status_code=200, content={"detail": "pong"})
    
    async def get_rec(self, request: BitrecsRequest):
        bt.logging.debug(f"API get_rec request:  {request.computed_body_hash}")
        bt.logging.debug(f"API get_rec request type:  {type(request)}")        

        try:            
            bt.logging.debug(f"API get_rec start forward")
            response = await self.forward_fn(request)
            #bt.logging.debug(f"API get_rec response: {response}")
            #bt.logging.debug(f"API get_rec response type: {type(response)}")

          #class ProductRecResponse:
            # user: str
            # original_query: str    
            # status_code: int
            # status_text: str
            # response_text: str
            # created_at: str
            # results: List[str]
            # models_used: List[str]
            # catalog_size: int
            # miner_uid: str
            # miner_public_key: str
            # reasoning: str
            bt.logging.debug(f"API get_rec response: {response.results}")
            final_recs = []
            for item in response.results:                
                item = item.rstrip('"').lstrip('"')
                bt.logging.trace(f"API get_rec item: {item}")                
                final_recs.append(item)
            
            #results = [json.loads(item.replace('"', '')) for item in response.results]

            bt.logging.trace(f"API get_rec final_recs: {final_recs}")

            bitrecs_rec = {
                    "user": response.user, 
                    "original_query": response.query,
                    "status_code": "200",
                    "status_text": "Success",
                    "response_text": "Success text",
                    "created_at": response.created_at,
                    "results": final_recs,
                    "models_used": response.models_used,
                    "catalog_size": "0",
                    "miner_uid": response.miner_uid,
                    "miner_hotkey": response.miner_hotkey,
                    "reasoning": "testing"
            }

            bt.logging.debug(f"API get_rec JSONResponse bitrecs_rec: {bitrecs_rec}")

            return JSONResponse(status_code=200, content=bitrecs_rec)

        except Exception as e:
            bt.logging.error(f"API get_rec error:  {e}")
            return JSONResponse(status_code=500,
                                content={"detail": "error", "status_code": 500})

    def start(self):
        self.fast_server.start()
        bt.logging.info(f"API server started at {self.fast_server.config.host}:{self.fast_server.config.port}")

        # if self.ngrok_domain is not None:
        #     self.tunnel = connect_ngrok_tunnel(
        #         local_port=self.fast_server.config.port,
        #         domain=self.ngrok_domain
        #     )

    def stop(self):
        self.fast_server.stop()
        bt.logging.info("API server stopped")

        # if self.tunnel is not None:
        #     ngrok.disconnect(
        #         public_url=self.tunnel.public_url
        #     )
        #     self.tunnel = None

    @staticmethod
    async def print_req(request: Request):        
        # Get request method
        method = request.method
        # Get request headers
        headers = request.headers
        # Get query parameters
        query_params = request.query_params
        # Get the body (awaitable for POST requests)
        body = await request.body()
        # Get the JSON body (if JSON is expected)
        try:
            json_body = await request.json()
        except Exception as e:
            json_body = None  # Not JSON or failed parsing
        return {
            "method": method,
            "headers": dict(headers),
            "query_params": dict(query_params),
            "body": body.decode("utf-8") if body else None,
            "json_body": json_body,
        }


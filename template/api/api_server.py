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
#from pyngrok import ngrok

ForwardFn = Callable[[BitrecsRequest], BitrecsRequest]

auth_data = dict()
request_counts = {}

def is_api_data_valid(data):
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


def load_api_config():
    bt.logging.debug("Loading API config")

    try:
        if not os.path.exists("template/api/api.json"):
            raise Exception(f"{'template/api/api.json'} does not exist")

        with open("template/api/api.json", 'r') as file:
            api_data = json.load(file)
            bt.logging.trace("api_data", api_data)

            valid, reason = is_api_data_valid(api_data)
            if not valid:
                raise Exception(f"{'neurons/api.json'} is poorly formatted. {reason}")
            if "change-me" in api_data["keys"]:
                bt.logging.warning("YOU ARE USING THE DEFAULT API KEY. CHANGE IT FOR SECURITY REASONS.")
        return api_data
    except Exception as e:
        bt.logging.error("Error loading API config:", e)
        traceback.print_exc()


async def auth_rate_limiting_middleware(request: Request, call_next):
    # Check if API key is valid
    # TODO use an official "auth key" header 
    # such that programs such as web browsers
    # know to hide this info from JavaScript and other environments.
    auth_api = request.headers.get('auth')
    auth_data = load_api_config()
    time_window = 60

    bt.logging.info("auth_data", auth_data)

    if auth_api not in auth_data["keys"].keys():
        bt.logging.debug(f"Unauthorized key: {auth_api}")
        return JSONResponse(status_code=401, content={"detail": "Unauthorized",
                                                      "translated_texts": []})

    requests_per_min = auth_data["keys"][auth_api]["requests_per_min"]

    # Rate limiting
    current_time = time.time()
    if auth_api in request_counts:
        requests, start_time = request_counts[auth_api]

        if current_time - start_time > time_window:
            # start a new time period
            request_counts[auth_api] = (1, current_time)
        elif requests < requests_per_min:
            # same time period
            request_counts[auth_api] = (requests + 1, start_time)
        else:
            bt.logging.debug(f"Rate limit exceeded for key: {auth_api}")
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded", "translated_texts": []})
    else:
        request_counts[auth_api] = (1, current_time)

    response = await call_next(request)
    return response

# def connect_ngrok_tunnel(local_port: int, domain: str) -> ngrok.NgrokTunnel:
#     auth_token = os.environ.get('NGROK_AUTH_TOKEN', None)
#     if auth_token is not None:
#         ngrok.set_auth_token(auth_token)

#     tunnel = ngrok.connect(
#         addr=str(local_port),
#         proto="http",
#         # Domain is required.
#         domain=domain
#     )
#     bt.logging.info(
#         f"API is available over NGROK at {tunnel.public_url}"
#     )

#     return tunnel


def _get_api_key(request: Request) -> Any:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    return auth_header


#@app.middleware("http")
async def api_key_validator(request, call_next) -> Response:
    if request.url.path in ["/favicon.ico"]:
        return await call_next(request)

    api_key = _get_api_key(request)
    if not api_key:
        return JSONResponse(
            status_code=400,
            content={"detail": "API key is missing"},
        )

    # with sql.get_db_connection() as conn:
    #     api_key_info = sql.get_api_key_info(conn, api_key)
    api_key_info = load_api_config()    

    if api_key_info is None:
        return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

    #credits_required = 1  # TODO: make this non-constant in the future???? (i.e. dependent on number of pools)????

    # Now check credits
    # if api_key_info[sql.BALANCE] is not None and api_key_info[sql.BALANCE] <= credits_required:
    #     return JSONResponse(
    #         status_code=HTTP_429_TOO_MANY_REQUESTS,
    #         content={"detail": "Insufficient credits - sorry!"},
    #     )

    # # Now check rate limiting
    # with sql.get_db_connection() as conn:
    #     rate_limit_exceeded = sql.rate_limit_exceeded(conn, api_key_info)
    #     if rate_limit_exceeded:
    #         return JSONResponse(
    #             status_code=HTTP_429_TOO_MANY_REQUESTS,
    #             content={"detail": "Rate limit exceeded - sorry!"},
    #         )

    response: Response = await call_next(request)

    # bt.logging.debug(f"response: {response}")
    # if response.status_code == 200:
    #     with sql.get_db_connection() as conn:
    #         sql.update_requests_and_credits(conn, api_key_info, credits_required)
    #         sql.log_request(conn, api_key_info, request.url.path, credits_required)
    #         conn.commit()
    return response




class ApiServer:
    app: FastAPI
    fast_server: FastAPIThreadedServer
    router: APIRouter
    forward_fn: ForwardFn
    #tunnel: Optional[ngrok.NgrokTunnel]
    #ngrok_domain: Optional[str]

    def __init__(
            self, 
            axon_port: int,
            forward_fn: ForwardFn,
            api_json: str,            
            #ngrok_domain: Optional[str]
    ):

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
        #self.ngrok_domain = ngrok_domain
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
            bt.logging.debug(f"API get_rec response: {response}")
            bt.logging.debug(f"API get_rec response type: {type(response)}")

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
            
            rec = {
                    "user": response.user, 
                    "original_query": response.query,
                    "status_code": "200",
                    "status_text": "Success",
                    "response_text": "Success text",
                    "created_at": response.created_at,
                    "results": response.results,
                    "models_used": response.models_used,
                    "catalog_size": "0",
                    "miner_uid": response.miner_uid,
                    "miner_hotkey": response.miner_hotkey,
                    "reasoning": "testing"
            }

            return JSONResponse(status_code=200, content=rec)

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


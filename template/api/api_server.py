import os
import json
import time
import uvicorn
import traceback
import bittensor as bt
import hmac
import hashlib
from typing import Callable, Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Request, APIRouter, Response, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from bittensor.core.axon import FastAPIThreadedServer
from template.protocol import BitrecsRequest
from template.commerce.product import Product
from template.api.api_counter import APICounter
from template.api.utils import api_key_validator
from template.utils import constants as CONST

ForwardFn = Callable[[BitrecsRequest], BitrecsRequest]

auth_data = dict()
request_counts = {}

SECRET_KEY = "change-me"


async def verify_request(request: BitrecsRequest, x_signature: str, x_timestamp: str):
    """
    Verify HMAC signature of the request   
   
    """

    # bt.logging.trace(f"API verify_request x_signature: {x_signature}")
    # bt.logging.trace(f"API verify_request x_timestamp: {x_timestamp}")

    d = {
        'created_at': request.created_at,
        'user': request.user,
        'num_results': request.num_results,
        'query': request.query,
        'context': request.context,
        'site_key': request.site_key,
        'results': request.results,
        'models_used': request.models_used,
        'miner_uid': request.miner_uid,
        'miner_hotkey': request.miner_hotkey
    }
    body_str = json.dumps(d, sort_keys=True)    
    string_to_sign = f"{x_timestamp}.{body_str}"    
    expected_signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Verify signature
    if not hmac.compare_digest(x_signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    timestamp = int(x_timestamp)
    current_time = int(time.time())
    if current_time - timestamp > 300:  # 5 minutes
        raise HTTPException(status_code=401, detail="Request expired")
    
    bt.logging.info(f"\033[1;32m Signature Verified\033[0m")
    


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
            self.generate_product_rec,
            methods=["POST"]
        )
        self.app.include_router(self.router)
        self.api_json = api_json #TODO not used

        self.api_counter = APICounter(
            os.path.join(self.app.root_path, "api_counter.json")
        )
        bt.logging.info(f"\033[1;33m API Counter set {self.api_counter.save_path} \033[0m")
        bt.logging.info(f"\033[1;32m API Server initialized \033[0m")

    
    async def ping(self):
        bt.logging.info(f"\033[1;32m API Server ping \033[0m")
        return JSONResponse(status_code=200, content={"detail": "pong"})
    
    
    async def generate_product_rec(
            self, 
            request: BitrecsRequest,
            x_signature: str = Header(...),
            x_timestamp: str = Header(...)
    ):  
        
        # headers = request.to_headers()
        # bt.logging.info(f"{headers}")

        try:
          
            await verify_request(request, x_signature, x_timestamp)

            stuff = Product.try_parse_context(request.context)
            catalog_size = len(stuff)
            bt.logging.trace(f"REQUEST CATALOG SIZE: {catalog_size}")
            if catalog_size < CONST.MIN_CATALOG_SIZE:
                bt.logging.error(f"API generate_product_rec catalog size too small")
                self.log_counter(False)
                return JSONResponse(status_code=500,
                                    content={"detail": "error - invalid catalog", "status_code": 500})
            
            st = time.time()
            response = await self.forward_fn(request)
            total_time = time.time() - st

            if len(response.results) == 0:
                bt.logging.error(f"API generate_product_rec response has no results")
                self.log_counter(False)
                return JSONResponse(status_code=500,
                                    content={"detail": "error", "status_code": 500})


            final_recs = []            
            # Remove single quotes from the string and convert items to JSON objects
            final_recs = [json.loads(idx.replace("'", '"')) for idx in response.results]
            #bt.logging.trace(f"API generate_product_rec final_recs: {final_recs}")
            response_text = "Bitrecs Took {:.2f} seconds to process this request".format(total_time)

            response = {
                "user": response.user, 
                "original_query": response.query,
                "status_code": "200",
                "status_text": "OK", #front end widgets expects this do not change
                "response_text": response_text,
                "created_at": response.created_at,
                "results": final_recs,
                "models_used": response.models_used,
                "catalog_size": str(catalog_size),
                "miner_uid": response.miner_uid,
                "miner_hotkey": response.miner_hotkey,
                "reasoning": "Bitrecs AI"
            }

            self.log_counter(True)
            #bt.logging.debug(f"API generate_product_rec JSONResponse bitrecs_rec: {bitrecs_rec}")
            return JSONResponse(status_code=200, content=response)

        except Exception as e:
            bt.logging.error(f"ERROR API generate_product_rec error:  {e}")
            self.log_counter(False)
            return JSONResponse(status_code=500,
                                content={"detail": "error", "status_code": 500})

    def start(self):
        self.fast_server.start()
        bt.logging.info(f"API server started at {self.fast_server.config.host}:{self.fast_server.config.port}")


    def stop(self):
        self.fast_server.stop()
        bt.logging.info("API server stopped")


    def log_counter(self, success: bool) -> None:
        try: 
            self.api_counter.update(is_success=success)
            self.api_counter.save()
        except Exception as e:
            bt.logging.error(f"ERROR API could not update counter log:  {e}")
            pass  

   


import time
import bittensor as bt
from fastapi import Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException

limiter = Limiter(key_func=get_remote_address)


@limiter.limit("60/minute")
async def filter_allowed_ips(self, request: Request, call_next) -> Response:
    try:
        if self.bypass_whitelist:
            response = await call_next(request)
            return response
    
        forwarded_for = request.headers.get("x-forwarded-for")
        if not forwarded_for:
            bt.logging.warning(f"Missing x-forwarded-for using get_remote_address ... ")
            forwarded_for = get_remote_address(request)
        
        bt.logging.trace(f"Resolved to: {forwarded_for}")

        if self.allowed_ips and forwarded_for not in self.allowed_ips:
            bt.logging.error(f"Blocked IP: {forwarded_for}")
            return Response(
                content="You do not have permission to access this resource",
                status_code=403,
            )
            
        bt.logging.trace(f"Allowed IP {forwarded_for}")
        response = await call_next(request)
        return response

    except RateLimitExceeded as e:
        bt.logging.warning(f"Rate limit exceeded for {forwarded_for}")
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "status_code": 429,
                "retry_after": 60
            },
            headers={"Retry-After": "60"}
        )



# def define_allowed_ips(self, url, netuid, min_stake):
#     while True:
#         try:
#             state = {}
#             all_allowed_ips = []
#             subtensor = bt.subtensor(url)
#             metagraph = subtensor.metagraph(netuid)
#             for uid in range(len(metagraph.total_stake)):
#                 if metagraph.total_stake[uid] > min_stake:
#                     all_allowed_ips.append(metagraph.axons[uid].ip)
#                     state[uid] = {
#                         "stake": metagraph.total_stake[uid].item(),
#                         "ip": metagraph.axons[uid].ip,
#                     }
#             self.allowed_ips = all_allowed_ips
#             # sort by stake
#             state = dict(
#                 sorted(state.items(), key=lambda item: item[1]["stake"], reverse=True)
#             )
#             print("Updated allowed ips", flush=True)
#             print(state)
#         except Exception as e:
#             print("Exception while updating allowed ips", str(e), flush=True)
#         time.sleep(60)



class OnlyJSONMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.method in ['POST']:
            response = await call_next(request)
            return response


        if 'application/json' not in request.headers.get('Content-Type', ''):
            return JSONResponse(
                status_code=415,
                content={
                    "detail": "Invalid Request",
                    "status_code": 415                    
                }                
            )
            #raise HTTPException(status_code=415, detail="Only JSON requests are accepted")
        
        try:            
            await request.json()
        except ValueError:            
            #raise HTTPException(status_code=400, detail="Invalid JSON in request body")
            return JSONResponse(
                status_code=415,
                content={
                        "detail": "Invalid Request",
                        "status_code": 415                    
                    }                
            )
        
        response = await call_next(request)
        return response
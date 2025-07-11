import time
import asyncio
from typing import Dict, List
from collections import defaultdict
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request, Depends

app = FastAPI(title="Rate Limiting Test With FastAPI", version="1.0.0")

class RateLimiter:
    """
    Rate Limiter using sliding window technique
    Tracks requests per IP address with configurable limits
    """
    def __init__(self):
        ## Storing request timestamps per IP address
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.max_requests = 5 ## Maximum requests allowed per IP -> 5 requests per minute
        self.time_window = 60  ## Time window in seconds -> 60 seconds (1 minute)
    
    def is_allowed(self, client_ip: str) -> tuple[bool, dict]:
        """
        Check if request is allowed based on rate limit
        Returns: (is_allowed, rate_limit_info)
        """
        current_time = time.time()
        
        ## Get request history for this IP
        request_times = self.requests[client_ip]
        
        ## Remove old requests outside the time window (sliding window)
        cutoff_time = current_time - self.time_window
        self.requests[client_ip] = [req_time for req_time in request_times if req_time > cutoff_time]
        
        ## Check if under rate limit
        current_request_count = len(self.requests[client_ip])
        
        if current_request_count < self.max_requests:
            self.requests[client_ip].append(current_time)
            remaining_requests = self.max_requests - (current_request_count + 1)
            
            return True, {
                "allowed": True,
                "requests_made": current_request_count + 1,
                "requests_remaining": remaining_requests,
                "reset_time": int(current_time + self.time_window),
                "retry_after": None
            }
        else:
            ## Rate limit exceeded
            oldest_request = min(self.requests[client_ip])
            retry_after = int((oldest_request + self.time_window) - current_time)
            
            return False, {
                "allowed": False,
                "requests_made": current_request_count,
                "requests_remaining": 0,
                "reset_time": int(oldest_request + self.time_window),
                "retry_after": max(1, retry_after)  
            }

## Rate limiter instance
rate_limiter = RateLimiter()

async def check_rate_limit(request: Request):
    """
    Dependency function to check rate limits
    This runs before the endpoint handler
    """
    client_ip = request.client.host
    is_allowed, rate_info = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again in {rate_info['retry_after']} seconds.",
                "rate_limit_info": rate_info
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": str(rate_info["requests_remaining"]),
                "X-RateLimit-Reset": str(rate_info["reset_time"]),
                "Retry-After": str(rate_info["retry_after"])
            }
        )
    
    return rate_info

## API Routes
@app.get("/")
async def root():
    """
    Basic endpoint without rate limiting for testing server status
    """
    return {
        "message": "FastAPI Rate Limiting App is running!",
        "endpoints": {
            "/protected": "Rate limited endpoint (5 requests/minute)",
            "/status": "Check your current rate limit status"
        }
    }

@app.get("/protected")
async def protected_endpoint(
    request: Request,
    rate_info: dict = Depends(check_rate_limit)
):
    """
    Protected endpoint with rate limiting
    Limited to 5 requests per minute per IP address
    """
    client_ip = request.client.host
    
    return {
        "message": "Success! You accessed the protected endpoint.",
        "client_ip": client_ip,
        "timestamp": time.time(),
        "rate_limit_info": rate_info,
        "data": {
            "secret_message": "This endpoint is protected by rate limiting!",
            "request_id": f"req_{int(time.time() * 1000)}"
        }
    }

@app.get("/status")
async def rate_limit_status(request: Request):
    """
    Check current rate limit status without consuming a request
    """
    client_ip = request.client.host
    current_time = time.time()
    
    ## Get current request count without adding new request
    request_times = rate_limiter.requests[client_ip]
    cutoff_time = current_time - rate_limiter.time_window
    active_requests = [req_time for req_time in request_times if req_time > cutoff_time]
    
    remaining_requests = rate_limiter.max_requests - len(active_requests)
    
    if active_requests:
        oldest_request = min(active_requests)
        reset_time = int(oldest_request + rate_limiter.time_window)
    else:
        reset_time = int(current_time + rate_limiter.time_window)
    
    return {
        "client_ip": client_ip,
        "rate_limit": {
            "max_requests": rate_limiter.max_requests,
            "time_window": rate_limiter.time_window,
            "requests_made": len(active_requests),
            "requests_remaining": max(0, remaining_requests),
            "reset_time": reset_time,
            "window_resets_in": max(0, reset_time - int(current_time))
        },
        "timestamp": current_time
    }

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc: HTTPException):
    """
    Custom handler for rate limit exceeded responses
    """
    return JSONResponse(
        status_code=429,
        content=exc.detail,
        headers=exc.headers
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

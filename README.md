# FastAPI Rate Limiting 

A robust FastAPI application demonstrating rate limiting implementation using a sliding window algorithm. This project showcases how to protect API endpoints from abuse by limiting the number of requests per client IP address.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Example Responses](#example-responses)

## Features

- **Sliding Window Rate Limiting**: More accurate than fixed window approaches
- **Per-IP Tracking**: Individual rate limits for each client IP address
- **Standard HTTP Headers**: Includes proper rate limiting response headers
- **Real-time Status**: Check current rate limit status without consuming requests
- **Robust Error Handling**: Clear error messages with retry information
- **Memory Efficient**: Automatic cleanup of expired request records
- **Production Ready**: Clean, well-documented code structure

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/CodeX-Addy/Rate_Limiting.git
   cd Rate_Limiting_Py
   ```

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

The server will start on `http://localhost:8000`

## Usage

### Quick Start
1. Start the server: `python main.py`
2. Visit `http://localhost:8000` for the main page
3. Test the protected endpoint: `http://localhost:8000/protected`
4. Check your rate limit status: `http://localhost:8000/status`

### Rate Limit Configuration
- **Limit**: 5 requests per minute per IP address
- **Algorithm**: Sliding window
- **Reset**: Automatic cleanup of expired requests

##  API Endpoints

### `GET /`
**Description**: Main page with API information  
**Rate Limit**: None  
**Response**: Basic API information and available endpoints

### `GET /protected`
**Description**: Protected endpoint with rate limiting  
**Rate Limit**: 5 requests per minute  
**Response**: Success message with rate limit information

### `GET /status`
**Description**: Check current rate limit status  
**Rate Limit**: None (doesn't consume requests)  
**Response**: Current rate limit statistics



### Error Response (HTTP 429)
When rate limit is exceeded, the API returns:
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again in X seconds.",
  "rate_limit_info": {
    "allowed": false,
    "requests_made": 5,
    "requests_remaining": 0,
    "reset_time": 1716547200,
    "retry_after": 30
  }
}
```

## Testing

### Manual Testing
1. **Test Normal Operation**:
   ```bash
   curl http://localhost:8000/protected
   ```

2. **Test Rate Limiting**:
   ```bash
   ## Make 6 rapid requests to trigger rate limiting
   for i in {1..6}; do curl http://localhost:8000/protected; echo; done
   ```

3. **Check Status**:
   ```bash
   curl http://localhost:8000/status
   ```

### Using Browser
1. Open `http://localhost:8000/protected`
2. Refresh the page rapidly 6 times
3. You'll see the rate limit error after the 5th request
4. Check `http://localhost:8000/status` to see current limits



## Example Responses

### Successful Request
```json
{
  "message": "Success! You accessed the protected endpoint.",
  "client_ip": "127.0.0.1",
  "timestamp": 1716547170.123,
  "rate_limit_info": {
    "allowed": true,
    "requests_made": 3,
    "requests_remaining": 2,
    "reset_time": 1716547230,
    "retry_after": null
  },
  "data": {
    "secret_message": "This endpoint is protected by rate limiting!",
    "request_id": "req_1716547170123"
  }
}
```

### Rate Limit Status
```json
{
  "client_ip": "127.0.0.1",
  "rate_limit": {
    "max_requests": 5,
    "time_window": 60,
    "requests_made": 3,
    "requests_remaining": 2,
    "reset_time": 1716547230,
    "window_resets_in": 45
  },
  "timestamp": 1716547185.456
}
```

## Few Performance Considerations

- **Memory Usage**: O(n) where n = number of active requests across all IPs
- **Time Complexity**: O(k) where k = requests per IP in time window
- **Scalability**: Suitable for small to medium applications
- **Production**: Can consider Redis-based solutions for distributed systems

## You can contribute as well-

1. Fork the repository
2. Create a feature branch: `git checkout -b branch-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add branch-name'`
5. Push to the branch: `git push origin branch-name`
6. Submit a pull request



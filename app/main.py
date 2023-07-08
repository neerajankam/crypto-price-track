from aiohttp import ClientError, ClientResponseError
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from custom_exceptions import APIKeyError, EncodeError, SignatureError
from routers import prices, trades, balances


app = FastAPI()
app.include_router(prices.router)
app.include_router(trades.router)
app.include_router(balances.router)


@app.exception_handler(EncodeError)
def handle_encode_error(request, err):
    return JSONResponse(
        status_code=err.status_code,
        content={"detail": err.detail},
    )


@app.exception_handler(APIKeyError)
def handle_api_key_error(request, err):
    return JSONResponse(
        status_code=err.status_code,
        content={"detail": err.detail},
    )


@app.exception_handler(SignatureError)
def handle_signature_error(request, err):
    return JSONResponse(
        status_code=err.status_code,
        content={"detail": err.detail},
    )


@app.exception_handler(Exception)
def handle_exception(request, err):
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


@app.exception_handler(ClientError)
def handle_aiohttp_client_error(request, err):
    return JSONResponse(status_code=err.status, content={"detail": err.message})


@app.exception_handler(ClientResponseError)
def handle_aiohttp_client_response_error(request, err):
    return JSONResponse(status_code=err.status, content={"detail": err.message})

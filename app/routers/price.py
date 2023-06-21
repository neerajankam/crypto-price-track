import os
import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import requests

from config import COINBASE_URL, GEMINI_URL, KRAKEN_URL
from exchanges.coinbase import Coinbase
from exchanges.kraken import Kraken
from exchanges.gemini import Gemini
from models.schemas import Item
from .utils import compute_total_price

router = APIRouter()


@router.get("/prices/{item}")
async def get_prices(item: Item, quantity: str):
    exchanges = [Coinbase(item), Kraken(item), Gemini(item)]
    asks = []
    bids = []
    for exchange in exchanges:
        bids.extend(await exchange.get_bid_price())
        asks.extend(await exchange.get_ask_price())

    bids.sort(key=lambda x: x["price"], reverse=True)
    asks.sort(key=lambda x: x["price"])

    buying_price = compute_total_price(asks, quantity)
    selling_price = compute_total_price(bids, quantity)

    return {
        "Crypto": item,
        "Quantity": quantity,
        "Buying price": buying_price,
        "Selling price": selling_price,
    }

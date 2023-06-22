import os
import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import requests

from exchanges.coinbase import Coinbase
from exchanges.kraken import Kraken
from exchanges.gemini import Gemini
from models.schemas import Item
from .utils import compute_total_price

router = APIRouter()


@router.get("/prices/{item}")
async def get_prices(item: Item, quantity: str):
    buying_price, selling_price = await get_buying_selling_prices(item, quantity)

    return {
        "Crypto": item,
        "Quantity": quantity,
        "Buying price": buying_price,
        "Selling price": selling_price,
    }


async def get_buying_selling_prices(item, quantity):
    coinbase_assets = await Coinbase.get_assets()
    gemini_assets = await Gemini.get_assets()
    kraken_assets = await Kraken.get_assets()

    exchanges = []
    if item in coinbase_assets:
        exchanges.append(Coinbase(item))
    if item in gemini_assets:
        exchanges.append(Gemini(item))
    if item in kraken_assets:
        exchanges.append(Kraken(item))
    asks = []
    bids = []
    for exchange in exchanges:
        bids.extend(await exchange.get_bid_price())
        asks.extend(await exchange.get_ask_price())

    bids.sort(key=lambda x: x["price"], reverse=True)
    asks.sort(key=lambda x: x["price"])

    buying_price = compute_total_price(asks, quantity)
    selling_price = compute_total_price(bids, quantity)
    return buying_price, selling_price

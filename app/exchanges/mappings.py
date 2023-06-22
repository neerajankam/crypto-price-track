import json

import asyncio

from app.config import COINBASE_ASSETS_URL, GEMINI_ASSETS_URL, KRAKEN_ASSETS_URL
from app.exchanges.utils import make_request

supported_cryptocurrencies = {"BTC", "ETH", "SOL"}


async def get_coinbase_assets():
    response = await make_request(COINBASE_ASSETS_URL)
    assets = {}
    for asset in response:
        if (
            asset["base_currency"] in supported_cryptocurrencies
            and asset["quote_currency"] == "USD"
        ):
            assets[asset["base_currency"]] = asset["id"]
    return assets


async def get_gemini_assets():
    response = await make_request(GEMINI_ASSETS_URL)
    assets = {}
    for asset in response:
        for crypto in supported_cryptocurrencies:
            if crypto + "USD" == asset.upper():
                assets[crypto] = asset.upper()
    return assets


async def get_kraken_assets():
    response = await make_request(KRAKEN_ASSETS_URL)
    response = response["result"]
    assets = {}
    for crypto in supported_cryptocurrencies:
        for asset in response.values():
            if asset["altname"] == crypto + "USD":
                assets[crypto] = crypto + "USD"
    assets["BTC"] = "XBTUSD"
    return assets


async def populate_mappings():
    coinbase_assets = await get_coinbase_assets()
    gemini_assets = await get_gemini_assets()
    kraken_assets = await get_kraken_assets()
    crypto_mappings = {"coinbase": {}, "kraken": {}, "gemini": {}}
    for crypto in supported_cryptocurrencies:
        crypto_mappings["coinbase"][crypto] = coinbase_assets[crypto]
        crypto_mappings["kraken"][crypto] = kraken_assets[crypto]
        crypto_mappings["gemini"][crypto] = gemini_assets[crypto]
    return crypto_mappings


if __name__ == "__main__":
    asyncio.run(populate_mappings()

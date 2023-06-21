import os
import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
import requests

from config import COINBASE_URL, GEMINI_URL, KRAKEN_URL
from exchanges.coinbase import Coinbase
from models.schemas import Item
from .utils import compute_total_price

router = APIRouter()


@router.get("/prices/{item}")
async def get_prices(item: Item, quantity: str):
    exchanges = [Coinbase(item)]
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


# def make_request(URL):
#     try:
#         response = requests.get(URL).json()
#     except Exception:
#         print(
#             "Encountered an exception while fetching orderbook information from: {}".format(
#                 URL
#             )
#         )
#     return response


# def structure_response(order_type, response, exchange):
#     if not order_type or not exchange or not response:
#         print(
#             "All three parameters {}, {}, {} are required to structure the response.".format(
#                 order_type, exchange, response
#             )
#         )
#     if order_type == "bids":
#         if exchange == "gemini":
#             response = [
#                 {"price": float(bid_dict["price"]), "amount": float(bid_dict["amount"])}
#                 for bid_dict in response["bids"]
#             ]
#         elif exchange == "kraken":
#             response = [
#                 {"price": float(bid[0]), "amount": float(bid[1])}
#                 for bid in response["result"]["XXBTZUSD"]["bids"]
#             ]
#         elif exchange == "coinbase":
#             response = [
#                 {"price": float(bid[0]), "amount": float(bid[1])}
#                 for bid in response["bids"]
#             ]
#     elif order_type == "asks":
#         if exchange == "gemini":
#             response = [
#                 {"price": float(ask["price"]), "amount": float(ask["amount"])}
#                 for ask in response["asks"]
#             ]
#         elif exchange == "kraken":
#             response = [
#                 {"price": float(ask[0]), "amount": float(ask[1])}
#                 for ask in response["result"]["XXBTZUSD"]["asks"]
#             ]
#         elif exchange == "coinbase":
#             response = [
#                 {"price": float(bid[0]), "amount": float(bid[1])}
#                 for bid in response["asks"]
#             ]
#     return response


# def get_all_asks():
#     coinbase_response = make_request(COINBASE_URL)
#     kraken_response = make_request(KRAKEN_URL)
#     gemini_response = make_request(GEMINI_URL)

#     coinbase_asks = structure_response("asks", coinbase_response, "coinbase")
#     kraken_asks = structure_response("asks", kraken_response, "kraken")
#     gemini_asks = structure_response("asks", gemini_response, "gemini")

#     all_asks = []
#     all_asks.extend(coinbase_asks)
#     all_asks.extend(kraken_asks)
#     all_asks.extend(gemini_asks)
#     all_asks.sort(key=lambda x: x["price"])

#     return all_asks


# def get_all_bids():
#     coinbase_response = make_request(COINBASE_URL)
#     kraken_response = make_request(KRAKEN_URL)
#     gemini_response = make_request(GEMINI_URL)

#     coinbase_bids = structure_response("bids", coinbase_response, "coinbase")
#     kraken_bids = structure_response("bids", kraken_response, "kraken")
#     gemini_bids = structure_response("bids", gemini_response, "gemini")

#     all_bids = []
#     all_bids.extend(coinbase_bids)
#     all_bids.extend(kraken_bids)
#     all_bids.extend(gemini_bids)
#     all_bids.sort(key=lambda x: x["price"], reverse=True)

#     return all_bids


# def get_buy_price_of_bitcoin(required_quantity):
#     all_asks = get_all_asks()
#     total_price = get_total_price(required_quantity, all_asks)
#     print("Total price to buy {} bitcoin is {}$".format(required_quantity, total_price))


# def get_sell_price_of_bitcoin(required_quantity):
#     all_bids = get_all_bids()
#     total_price = get_total_price(required_quantity, all_bids)
#     print(
#         "Total price I get if I sell {} bitcoin is {}$".format(
#             required_quantity, total_price
#         )
#     )


# buy_quantity = input("Enter the quantity of bitcoin you want to buy: ")
# get_buy_price_of_bitcoin(float(buy_quantity))

# sell_quantity = input("Enter the quantity of bitcoin you want to sell: ")
# get_sell_price_of_bitcoin(float(sell_quantity))

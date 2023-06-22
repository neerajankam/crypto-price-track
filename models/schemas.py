from enum import Enum

from fastapi import FastAPI


class Item(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    SOL = "SOL"
    XRP = "XRP"
    LRC = "LRC"

from enum import Enum

from fastapi import FastAPI


class Item(str, Enum):
    BTC = "BTC"

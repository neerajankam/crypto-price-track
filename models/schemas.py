from enum import Enum


class Crypto(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    SOL = "SOL"
    XRP = "XRP"
    LRC = "LRC"


class PriceType(str, Enum):
    individual = "individual"
    consolidated = "consolidated"

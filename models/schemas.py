from enum import Enum


class Crypto(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    SOL = "SOL"
    XRP = "XRP"
    LRC = "LRC"


class ViewType(str, Enum):
    individual = "individual"
    consolidated = "consolidated"


class Exchange(str, Enum):
    coinbase = "coinbase"
    kraken = "kraken"

from abc import ABC, abstractmethod


class ExchangeInterface(ABC):
    @abstractmethod
    def get_bid_price():
        pass

    @abstractmethod
    def get_ask_price():
        pass

    @classmethod
    def get_assets():
        pass

    @abstractmethod
    def get_trades():
        pass

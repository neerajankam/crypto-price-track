from abc import ABC, abstractmethod


class ExchangeInterface(ABC):
    @abstractmethod
    def get_bid_price():
        pass

    @abstractmethod
    def get_ask_price():
        pass

    @abstractmethod
    def make_request():
        pass

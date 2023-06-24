from urls import GEMINI_PRICE_URL, GEMINI_ASSETS_URL, GEMINI_TRADES_URL
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper, structure_gemini
from app.supported_cryptos import NAMES
from logger.app_logger import logger
from typing import List, Dict, Any


class Gemini(ExchangeInterface):
    __price_url = GEMINI_PRICE_URL
    __assets_url = GEMINI_ASSETS_URL
    __trades_url = GEMINI_TRADES_URL
    __assets = {}

    def __init__(self, crypto_pair: str) -> None:
        """
        Initializes a Gemini instance.

        :param crypto_pair: The crypto pair.
        :type crypto_pair: str
        """
        self.crypto_pair = crypto_pair

    @classmethod
    async def get_assets(cls) -> Dict[str, str]:
        """
        Retrieves the assets from Gemini.

        :raises Exception: If an error occurs while fetching the assets.

        :return: The assets dictionary.
        :rtype: Dict[str, str]
        """
        if not cls.__assets:
            try:
                response = await request_helper(cls.__assets_url)
            except Exception:
                logger.exception(f"Error while fetching assets from {cls.__assets_url}")
                raise Exception(f"Error while fetching assets from {cls.__assets_url}")
            assets = {}
            for asset in response:
                for crypto in NAMES:
                    if crypto + "USD" == asset.upper():
                        assets[crypto] = asset.upper()
            cls.__assets = assets
        return cls.__assets

    async def get_trades(self, limit: int) -> List[Dict[str, Any]]:
        """
        Retrieve trades from Gemini exchange.

        :param limit: The maximum number of trades to retrieve.
        :type limit: int
        :return: A list of structured trades.
        :rtype: List[Dict[str, Any]]
        """
        complete_url = Gemini.__trades_url.format(
            Gemini.__assets[self.crypto_pair], limit
        )
        response = await request_helper(complete_url)
        structured_response = structure_gemini(response)
        return structured_response

    async def get_bid_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the bid prices from Gemini.

        :return: The bid prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Gemini.__price_url.format(Gemini.__assets[self.crypto_pair])
        response = await request_helper(complete_url)
        response = [
            {"price": float(bid["price"]), "amount": float(bid["amount"])}
            for bid in response["bids"]
        ]
        return response

    async def get_ask_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the ask prices from Gemini.

        :return: The ask prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Gemini.__price_url.format(Gemini.__assets[self.crypto_pair])
        response = await request_helper(complete_url)
        response = [
            {"price": float(ask["price"]), "amount": float(ask["amount"])}
            for ask in response["asks"]
        ]
        return response

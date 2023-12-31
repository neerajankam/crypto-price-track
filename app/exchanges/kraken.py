import base64
import hashlib
import hmac
import os
import time
import urllib

from app.supported_cryptos import NAMES
from custom_exceptions import APIKeyError, EncodeError, SignatureError
from urls import (
    KRAKEN_PRICE_URL,
    KRAKEN_ASSETS_URL,
    KRAKEN_TRADES_URL,
    KRAKEN_BALANCES_URL,
    KRAKEN_BALANCES_POSTFIX,
)
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper, structure_kraken
from logger.app_logger import logger
from typing import Any, Dict, List, Optional, Union


class Kraken(ExchangeInterface):
    price_url = KRAKEN_PRICE_URL
    assets_url = KRAKEN_ASSETS_URL
    trades_url = KRAKEN_TRADES_URL
    balances_url = KRAKEN_BALANCES_URL
    assets = None

    def __init__(self, crypto_pair: str) -> None:
        """
        Initializes a Kraken instance.

        :param crypto_pair: The crypto pair.
        :type crypto_pair: str
        """
        self.crypto_pair = crypto_pair

    @classmethod
    async def get_assets(cls) -> Dict[str, str]:
        """
        Retrieves the assets from Kraken.

        :raises Exception: If an error occurs while fetching the assets.

        :return: The assets dictionary.
        :rtype: Dict[str, str]
        """
        if not cls.assets:
            response = await request_helper(cls.assets_url, "GET")
            if not isinstance(response, dict):
                return response
            response = response["result"]
            assets = {}
            for crypto in NAMES:
                for asset in response.values():
                    if asset["altname"] == crypto + "USD":
                        assets[crypto] = crypto + "USD"
            assets["BTC"] = "XXBTZUSD"
            assets["ETH"] = "XETHZUSD"
            cls.assets = assets
        return cls.assets

    async def get_trades(self, limit: int) -> List[Dict[str, Any]]:
        """
        Retrieve trades from Kraken exchange.

        :param limit: The maximum number of trades to retrieve.
        :type limit: int
        :return: A list of structured trades.
        :rtype: List[Dict[str, Any]]
        """
        complete_url = Kraken.trades_url.format(Kraken.assets[self.crypto_pair], limit)
        response = await request_helper(complete_url, "GET")
        structured_response = structure_kraken(
            response, Kraken.assets[self.crypto_pair]
        )
        return structured_response

    async def get_bid_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the bid prices from Kraken.

        :return: The bid prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Kraken.price_url.format(Kraken.assets[self.crypto_pair])
        response = await request_helper(complete_url, "GET")
        response = [
            {"price": float(bid[0]), "amount": float(bid[1])}
            for bid in response["result"][Kraken.assets[self.crypto_pair]]["bids"]
        ]
        return response

    async def get_ask_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the ask prices from Kraken.

        :return: The ask prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Kraken.price_url.format(Kraken.assets[self.crypto_pair])
        response = await request_helper(complete_url, "GET")
        response = [
            {"price": float(ask[0]), "amount": float(ask[1])}
            for ask in response["result"][Kraken.assets[self.crypto_pair]]["asks"]
        ]
        return response

    @classmethod
    async def get_balance_details(cls) -> dict:
        """
        Get balance details from Kraken exchange.

        :return: The balance details.
        :rtype: dict
        """
        data = {"nonce": str(int(1000 * time.time()))}
        headers = cls.get_authorization_headers(data)
        response = await request_helper(cls.balances_url, "POST", headers, data)
        return response["result"]

    @classmethod
    def get_authorization_headers(cls, data: dict) -> Optional[dict]:
        """
        Get the authorization headers for Kraken API requests.

        :param data: The data to include in the request.
        :type data: dict
        :return: The authorization headers or None if there was an error.
        :rtype: Optional[dict]
        """
        try:
            api_key = os.environ["KRAKEN_API_KEY"]
            secret_key = os.environ["KRAKEN_SECRET_KEY"]
        except KeyError:
            logger.exception(
                "Kraken keys needs to be set to be able to make the API call."
            )
            raise APIKeyError(
                status_code=500,
                detail="Kraken keys needs to be set to be able to make the API call.",
            )
        signature = cls.get_signature(KRAKEN_BALANCES_POSTFIX, data, secret_key)
        return {"API-Key": api_key, "API-Sign": signature}

    @classmethod
    def get_signature(cls, url: str, data: dict, secret: str) -> Optional[str]:
        """
        Get the signature for Kraken API requests.

        :param url: The URL of the request.
        :type url: str
        :param data: The data to include in the request.
        :type data: dict
        :param secret: The secret key for the API.
        :type secret: str
        :return: The signature or None if there was an error.
        :rtype: Optional[str]
        """
        try:
            postdata = urllib.parse.urlencode(data)
            encoded = (str(data["nonce"]) + postdata).encode()
            message = url.encode() + hashlib.sha256(encoded).digest()

            mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
            sigdigest = base64.b64encode(mac.digest())
        except TypeError:
            logger.exception("Error while serializing kraken data.")
            raise TypeError("Error while serializing kraken data.")
        except Exception:
            logger.exception("Encountered error while building kraken signature.")
            raise SignatureError(
                status_code=500,
                detail="Error encountered while building gemini signature and payload.",
            )
        return sigdigest.decode()

import hashlib
import hmac
import os
import time

from fastapi.responses import Response

from urls import (
    COINBASE_PRICE_URL,
    COINBASE_ASSETS_URL,
    COINBASE_TRADES_URL,
    COINBASE_BALANCES_URL,
)
from .exchange_interface import ExchangeInterface
from .utils import make_request as request_helper, structure_coinbase
from app.supported_cryptos import NAMES
from logger.app_logger import logger
from typing import Any, Dict, List, Union


class Coinbase(ExchangeInterface):
    __price_url = COINBASE_PRICE_URL
    __assets_url = COINBASE_ASSETS_URL
    __trades_url = COINBASE_TRADES_URL
    __balances_url = COINBASE_BALANCES_URL
    __assets = {}

    def __init__(self, crypto_pair: str) -> None:
        """
        Initializes a Coinbase instance.

        :param crypto_pair: The crypto pair.
        :type crypto_pair: str
        """
        self.crypto_pair = crypto_pair

    async def get_trades(self, limit: int) -> List[Dict[str, Any]]:
        """
        Retrieve trades from Coinbase exchange.

        :param limit: The maximum number of trades to retrieve.
        :type limit: int
        :return: A list of structured trades.
        :rtype: List[Dict[str, Any]]
        """
        complete_url = Coinbase.__trades_url.format(
            Coinbase.__assets[self.crypto_pair], limit
        )
        response = await request_helper(complete_url, "GET")
        structured_response = structure_coinbase(response)
        return structured_response

    async def get_bid_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the bid prices from Coinbase.

        :return: The bid prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Coinbase.__price_url.format(Coinbase.__assets[self.crypto_pair])
        response = await request_helper(complete_url, "GET")
        response = [
            {"price": float(bid[0]), "amount": float(bid[1])}
            for bid in response["bids"]
        ]
        return response

    async def get_ask_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the ask prices from Coinbase.

        :return: The ask prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Coinbase.__price_url.format(Coinbase.__assets[self.crypto_pair])
        response = await request_helper(complete_url, "GET")
        response = [
            {"price": float(ask[0]), "amount": float(ask[1])}
            for ask in response["asks"]
        ]
        return response

    @classmethod
    async def get_assets(cls) -> Dict[str, str]:
        """
        Retrieves the assets from Coinbase.

        :raises Exception: If an error occurs while fetching the assets.

        :return: The assets dictionary.
        :rtype: Dict[str, str]
        """
        if not cls.__assets:
            response = await request_helper(cls.__assets_url, "GET")
            assets = {}
            for asset in response:
                if asset["base_currency"] in NAMES and asset["quote_currency"] == "USD":
                    assets[asset["base_currency"]] = asset["id"]
            cls.__assets = assets
        return cls.__assets

    @classmethod
    async def get_balance_details(cls):
        headers = cls.get_authorization_headers(cls.__balances_url, None, "GET")
        if not headers:
            return Response(
                content={
                    "Error while fetching coinbase authorization details.",
                },
                status_code=500,
            )
        response = await request_helper(cls.__balances_url, "GET", headers)
        return response

    @classmethod
    def get_authorization_headers(cls, url, body, request_method):
        timestamp = str(int(time.time()))
        message = timestamp + request_method + url + (body or "")
        try:
            encoded_message = message.encode("utf-8")
        except UnicodeEncodeError:
            logger.exception(
                "Failed to encode the message while grabbing coinbase authorization headers."
            )
            return None
        try:
            api_key = os.environ["COINBASE_API_KEY"]
            secret_key = os.environ["COINBASE_SECRET_KEY"]
        except KeyError:
            logger.exception(
                "Coinbase keys needs to be set to be able to make the API call."
            )
            return None

        secret_key_bytes = secret_key.encode("utf-8")

        signature = hmac.new(
            secret_key_bytes, encoded_message, hashlib.sha256
        ).hexdigest()

        return {
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-KEY": api_key,
        }

import base64
import hashlib
import hmac
from fastapi.responses import Response
import json
import os
import time

from app.supported_cryptos import NAMES
from custom_exceptions import APIKeyError, EncodeError, SignatureError
from urls import (
    GEMINI_PRICE_URL,
    GEMINI_ASSETS_URL,
    GEMINI_TRADES_URL,
    GEMINI_BALANCES_URL,
    GEMINI_BALANCES_POSTFIX,
)
from .exchange_interface import ExchangeInterface
from .utils import (
    make_request as request_helper,
    make_request_synchronous as request_helper_sync,
    structure_gemini,
)
from logger.app_logger import logger
from typing import Any, Dict, List, Optional, Union


class Gemini(ExchangeInterface):
    price_url = GEMINI_PRICE_URL
    assets_url = GEMINI_ASSETS_URL
    trades_url = GEMINI_TRADES_URL
    balances_url = GEMINI_BALANCES_URL
    assets = {}

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
        if not cls.assets:
            response = await request_helper(cls.assets_url)
            assets = {}
            for asset in response:
                for crypto in NAMES:
                    if crypto + "USD" == asset.upper():
                        assets[crypto] = asset.upper()
            cls.assets = assets
        return cls.assets

    async def get_trades(self, limit: int) -> List[Dict[str, Any]]:
        """
        Retrieve trades from Gemini exchange.

        :param limit: The maximum number of trades to retrieve.
        :type limit: int
        :return: A list of structured trades.
        :rtype: List[Dict[str, Any]]
        """
        complete_url = Gemini.trades_url.format(Gemini.assets[self.crypto_pair], limit)
        response = await request_helper(complete_url)
        structured_response = structure_gemini(response)
        return structured_response

    async def get_bid_price(self) -> List[Dict[str, float]]:
        """
        Retrieves the bid prices from Gemini.

        :return: The bid prices.
        :rtype: List[Dict[str, float]]
        """
        complete_url = Gemini.price_url.format(Gemini.assets[self.crypto_pair])
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
        complete_url = Gemini.price_url.format(Gemini.assets[self.crypto_pair])
        response = await request_helper(complete_url)
        response = [
            {"price": float(ask["price"]), "amount": float(ask["amount"])}
            for ask in response["asks"]
        ]
        return response

    @classmethod
    async def get_balance_details(cls) -> Union[dict, Response]:
        """
        Get balance details from the Gemini exchange.

        :return: The balance details or an error response.
        :rtype: Union[dict, Response]
        """
        data = {
            "nonce": str(int(time.time())),
            "request": GEMINI_BALANCES_POSTFIX,
        }
        headers = cls.get_authorization_headers(data)
        response = request_helper_sync(cls.balances_url, "POST", headers, data)
        return response

    @classmethod
    def get_authorization_headers(cls, data: dict) -> Optional[dict]:
        """
        Get the authorization headers for Gemini API requests.

        :param data: The data to include in the request.
        :type data: dict
        :return: The authorization headers or None if there was an error.
        :rtype: Optional[dict]
        """
        try:
            api_key = os.environ["GEMINI_API_KEY"]
            secret_key = os.environ["GEMINI_SECRET_KEY"]
        except KeyError:
            logger.exception(
                "Gemini keys needs to be set to be able to make the API call."
            )
            raise APIKeyError(
                status_code=500,
                detail="Gemini keys needs to be set to be able to make the API call.",
            )
        payload, signature = cls.get_payload_and_signature(data, secret_key)
        return {
            "X-GEMINI-APIKEY": api_key,
            "X-GEMINI-PAYLOAD": payload,
            "X-GEMINI-SIGNATURE": signature,
        }

    @classmethod
    def get_payload_and_signature(cls, data: dict, secret_key: str) -> Optional[tuple]:
        """
        Get the payload and signature for Gemini API requests.

        :param data: The data to include in the request.
        :type data: dict
        :param secret_key: The secret key for the API.
        :type secret_key: str
        :return: The payload and signature or None if there was an error.
        :rtype: Optional[tuple]
        """
        try:
            encoded_payload = json.dumps(data).encode()
            payload_b64 = base64.b64encode(encoded_payload)
            secret_key_bytes = secret_key.encode("utf-8")
            signature = hmac.new(
                secret_key_bytes, payload_b64, hashlib.sha384
            ).hexdigest()
        except TypeError:
            logger.exception("Error while serializing gemini data.")
            raise TypeError("Error while serializing gemini data.")
        except UnicodeEncodeError:
            logger.exception("Encountered error while building gemini signature.")
            raise EncodeError(
                status_code=500,
                detail="Failed to encode the message while building gemini authorization headers.",
            )
        except Exception:
            logger.exception(
                "Error encountered while building gemini signature and payload."
            )
            raise SignatureError(
                status_code=500,
                detail="Error encountered while building gemini signature and payload.",
            )
        return payload_b64, signature

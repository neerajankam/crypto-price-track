from copy import deepcopy

import aiohttp
from aiohttp import ClientError, ClientResponseError
from fastapi import Response
import requests

from logger.app_logger import logger
from typing import Any, Dict, Optional, List, Union


individual_trade_response = {
    "trade_id": None,
    "side": None,
    "size": None,
    "price": None,
}


async def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict] = None,
    data: Optional[Dict] = None,
) -> Union[dict, Response]:
    """
    Makes an HTTP request to the specified URL.

    :param url: The URL to make the request to.
    :type url: str
    :param method: The HTTP method to use (GET or POST).
    :type method: str
    :param headers: The headers to include in the request.
    :type headers: Optional[Dict]
    :param data: The data to send in the request body (for POST method).
    :type data: Optional[Dict]
    :return: The JSON response data.
    :rtype: Dict[str, Any]
    :raises ClientError: If an error occurs during the request.
    :raises Exception: If an exception occurs during the request.
    """
    try:
        async with aiohttp.ClientSession() as session:
            if method.upper() == "GET":
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
            elif method.upper() == "POST":
                async with session.post(url, headers=headers, data=data) as response:
                    response_json = await response.json()
                    response.raise_for_status()
            else:
                raise ValueError(
                    "Invalid HTTP method. Only GET and POST are supported."
                )

            response_json = await response.json()
        return response_json
    except ClientResponseError as e:
        return Response(content=str(e.message), status_code=e.status)
    except ClientError as e:
        logger.exception(f"Error while making the request to {url}")
        return Response(content=str(e.message), status_code=e.status)
    except Exception as e:
        logger.exception(f"Encountered exception while making request to {url}")
        return Response(content=str(e), status_code=500)


def make_request_synchronous(
    url: str, method: str, headers: Optional[Dict] = None, data: Optional[Dict] = None
) -> Union[dict, Response]:
    """
    Make a synchronous HTTP request to the specified URL.

    :param url: The URL to make the request to.
    :type url: str
    :param method: The HTTP method to use (POST or GET).
    :type method: str
    :param headers: The headers to include in the request.
    :type headers: Optional[Dict]
    :param data: The data to include in the request (for POST requests).
    :type data: Optional[Dict]
    :return: The JSON response data.
    :rtype: dict
    """
    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, data=data)
        elif method.upper() == "GET":
            response = response.get(url, headers=headers)
        status_code = response.status_code
        response_data = response.json()

        if response_data:
            return response_data
        else:
            return Response(content="No balances to show.", status_code=status_code)

    except requests.RequestException as e:
        return Response(content=str(e), status_code=500)
    except Exception as e:
        return Response(content=str(e), status_code=500)


def structure_coinbase(trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Structure trades from Coinbase exchange.

    :param trades: The trades data to be structured.
    :type trades: List[Dict[str, Any]]
    :return: A list of structured trades.
    :rtype: List[Dict[str, Any]]
    """
    structured_trades = []
    for trade in trades:
        for key in individual_trade_response:
            individual_trade_response[key] = trade[key]
        structured_trades.append(deepcopy(individual_trade_response))
    return structured_trades


def structure_gemini(trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Structure trades from Gemini exchange.

    :param trades: The trades data to be structured.
    :type trades: List[Dict[str, Any]]
    :return: A list of structured trades.
    :rtype: List[Dict[str, Any]]
    """
    structured_trades = []
    for trade in trades:
        individual_trade_response["trade_id"] = trade["tid"]
        individual_trade_response["side"] = trade["type"]
        individual_trade_response["size"] = trade["amount"]
        individual_trade_response["price"] = trade["price"]
        structured_trades.append(deepcopy(individual_trade_response))
    return structured_trades


def structure_kraken(trades: Dict[str, Any], crypto_pair: str) -> List[Dict[str, Any]]:
    """
    Structure trades from Kraken exchange.

    :param trades: The trades data to be structured.
    :type trades: Dict[str, Any]
    :param crypto_pair: The crypto pair.
    :type crypto_pair: str
    :return: A list of structured trades.
    :rtype: List[Dict[str, Any]]
    """
    trades = trades["result"][crypto_pair]
    structured_trades = []
    for trade in trades:
        individual_trade_response["trade_id"] = trade[6]
        individual_trade_response["side"] = "buy" if trade[3] == "b" else "sell"
        individual_trade_response["size"] = trade[1]
        individual_trade_response["price"] = trade[0]
        structured_trades.append(deepcopy(individual_trade_response))
    return structured_trades

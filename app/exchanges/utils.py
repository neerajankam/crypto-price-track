from copy import deepcopy

import aiohttp
from aiohttp import ClientError
from logger.app_logger import logger
from typing import Any, Dict, List


individual_trade_response = {
    "trade_id": None,
    "side": None,
    "size": None,
    "price": None,
}


async def make_request(url: str) -> Dict[str, Any]:
    """
    Makes an HTTP GET request to the specified URL.

    :param url: The URL to make the request to.
    :type url: str
    :return: The JSON response data.
    :rtype: Dict[str, Any]
    :raises ClientError: If an error occurs during the request.
    :raises Exception: If an exception occurs during the request.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                response_json = await response.json()
        return response_json
    except ClientError as e:
        logger.exception(f"Error while making the request to {url}")
        raise ClientError(f"Error while making the request to {url}")
    except Exception:
        logger.exception(f"Encountered exception while making request to {url}")
        raise Exception(f"Encountered exception while making request to {url}")


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

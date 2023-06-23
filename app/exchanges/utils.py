import aiohttp
from aiohttp import ClientError
from logger.app_logger import logger
from typing import Dict, Any


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

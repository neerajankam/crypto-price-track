from exchanges.coinbase import Coinbase
from exchanges.exchange_interface import ExchangeInterface
from exchanges.kraken import Kraken
from exchanges.gemini import Gemini
from logger.app_logger import logger
from typing import Any, Dict, List, Optional, Tuple, Type


EXCHANGE_MAP = {
    Coinbase: "coinbase",
    Gemini: "gemini",
    Kraken: "kraken",
}


async def get_consolidated_prices(crypto: str, quantity: float) -> Tuple[float, float]:
    """
    Get consolidated buying and selling prices across all supported exchanges.

    :param crypto: The cryptocurrency.
    :type crypto: str
    :param quantity: The quantity.
    :type quantity: float
    :return: The buying price and selling price.
    :rtype: Tuple[float, float]
    """
    exchanges = await get_supported_exchanges(crypto)

    for exchange in exchanges:
        bids = await get_sorted_exchange_prices(exchange, crypto, True)
        asks = await get_sorted_exchange_prices(exchange, crypto, False)

    buying_price = compute_total_price(asks, quantity)
    selling_price = compute_total_price(bids, quantity)

    return buying_price, selling_price


async def get_all_exchanges_prices(
    crypto: str, quantity: float
) -> Dict[str, Dict[str, Any]]:
    """
    Get prices from all supported exchanges.

    :param crypto: The cryptocurrency.
    :type crypto: str
    :param quantity: The quantity.
    :type quantity: float
    :return: The prices from all exchanges.
    :rtype: Dict[str, Dict[str, Any]]
    """
    exchanges = await get_supported_exchanges(crypto)
    response = empty_prices_response()

    for exchange in exchanges:
        if exchange in EXCHANGE_MAP:
            exchange_key = EXCHANGE_MAP[exchange]
            buying_price = await get_sorted_exchange_prices(exchange, crypto, True)
            selling_price = await get_sorted_exchange_prices(exchange, crypto, False)

            response[exchange_key]["buying_price"] = compute_total_price(
                buying_price, quantity
            )
            response[exchange_key]["selling_price"] = compute_total_price(
                selling_price, quantity
            )

    return response


async def get_all_exchanges_trades(crypto: str, limit: int) -> Dict[str, Any]:
    """
    Get trades from all supported exchanges.

    :param crypto: The cryptocurrency.
    :type crypto: str
    :param limit: The limit.
    :type limit: int
    :return: The trades from all exchanges.
    :rtype: Dict[str, Any]
    """
    import copy

    exchanges = await get_supported_exchanges(crypto)
    trades = {}
    for exchange in exchanges:
        if exchange in EXCHANGE_MAP:
            exchange_key = EXCHANGE_MAP[exchange]
            response = await exchange(crypto).get_trades(limit)
            trades[exchange_key] = copy.deepcopy(response)
    return trades


async def get_supported_exchanges(crypto: str) -> List[Type[ExchangeInterface]]:
    """
    Get the supported exchanges for a given cryptocurrency.

    :param crypto: The cryptocurrency.
    :type crypto: str
    :return: The supported exchanges.
    :rtype: List[Type[ExchangeInterface]]
    """
    try:
        assets = await get_assets()
        exchanges = []
        for exchange in EXCHANGE_MAP:
            exchange_name = EXCHANGE_MAP[exchange]
            if crypto in assets[exchange_name]:
                exchanges.append(exchange)

    except Exception:
        logger.exception("Encountered exception while fetching supported assets.")
        raise FetchAssetsError(
            "Error while fetching the supported assets from exchanges."
        )

    return exchanges


async def get_assets() -> Dict[str, Dict[str, Any]]:
    """
    Get the assets from all exchanges.

    :return: The assets from all exchanges.
    :rtype: Dict[str, Dict[str, Any]]
    """
    assets = {}
    for exchange in EXCHANGE_MAP:
        exchange_name = EXCHANGE_MAP[exchange]
        assets[exchange_name] = await exchange.get_assets()
    return assets


def compute_total_price(
    offers: List[Dict[str, Any]], required_quantity: float
) -> float:
    """
    Compute the total price based on the offers and required quantity.

    :param offers: The offers.
    :type offers: List[Dict[str, Any]]
    :param required_quantity: The required quantity.
    :type required_quantity: float
    :return: The total price.
    :rtype: float
    """
    quantity_so_far = 0
    total_price = 0
    required_quantity = float(required_quantity)
    for offer in offers:
        current_price = offer["price"]
        current_quantity = offer["amount"]
        if quantity_so_far <= required_quantity:
            if current_quantity > required_quantity - quantity_so_far:
                total_price += (required_quantity - quantity_so_far) * current_price
                break
            else:
                total_price += current_quantity * current_price
                quantity_so_far += current_quantity
    return total_price


def empty_prices_response() -> Dict[str, Dict[str, Optional[float]]]:
    """
    Create an empty prices response.

    :return: The empty prices response.
    :rtype: Dict[str, Dict[str, Optional[float]]]
    """
    return {
        "coinbase": {"buying_price": None, "selling_price": None},
        "gemini": {"buying_price": None, "selling_price": None},
        "kraken": {"buying_price": None, "selling_price": None},
    }


async def get_sorted_exchange_prices(
    exchange: Type[ExchangeInterface], crypto: str, is_buying_price: bool
) -> List[Dict[str, Any]]:
    """
    Get sorted exchange prices for a given cryptocurrency.

    :param exchange: The exchange.
    :type exchange: Type[ExchangeInterface]
    :param crypto: The cryptocurrency.
    :type crypto: str
    :param is_buying_price: Indicates whether it's a buying price or not.
    :type is_buying_price: bool
    :return: The sorted exchange prices.
    :rtype: List[Dict[str, Any]]
    """
    try:
        prices = (
            await exchange(crypto).get_bid_price()
            if is_buying_price
            else await exchange(crypto).get_ask_price()
        )
    except Exception:
        logger.exception("Encountered exception while fetching the bid and ask prices.")
        raise FetchPricesError(
            f"Error while fetching the bid and ask prices of {crypto.value} from exchanges."
        )
    sort_prices(prices, is_buying_price)
    return prices


def sort_prices(prices: List[Dict[str, Any]], reverse: bool = False) -> None:
    """
    Sort the prices.

    :param prices: The prices.
    :type prices: List[Dict[str, Any]]
    :param reverse: Indicates whether to sort in reverse order or not.
    :type reverse: bool, optional
    """
    prices.sort(key=lambda x: x["price"], reverse=reverse)


async def get_balance_details(exchange):
    for exchange_class in EXCHANGE_MAP:
        if exchange == EXCHANGE_MAP[exchange_class]:
            response = await exchange_class.get_balance_details()
    return response


class FetchAssetsError(Exception):
    pass


class FetchPricesError(Exception):
    pass

from exchanges.coinbase import Coinbase
from exchanges.kraken import Kraken
from exchanges.gemini import Gemini
from logger.app_logger import logger


EXCHANGE_MAP = {
    Coinbase: "coinbase",
    Gemini: "gemini",
    Kraken: "kraken",
}


async def get_consolidated_prices(crypto, quantity):
    exchanges = await get_supported_exchanges(crypto)

    for exchange in exchanges:
        bids = [await get_sorted_exchange_prices(exchange, crypto, True)]
        asks = [await get_sorted_exchange_prices(exchange, crypto, False)]

    buying_price = compute_total_price(asks, quantity)
    selling_price = compute_total_price(bids, quantity)

    return buying_price, selling_price


async def get_all_exchanges_prices(crypto, quantity):
    exchanges = await get_supported_exchanges(crypto)
    response = create_initial_response()

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


async def get_supported_exchanges(crypto):
    try:
        assets = await get_assets()
    except Exception:
        logger.exception("Encountered exception while fetching supported assets.")
        raise FetchAssetsError(
            "Error while fetching the supported assets from exchanges."
        )
    exchanges = []
    for exchange in EXCHANGE_MAP:
        exchange_name = EXCHANGE_MAP[exchange]
        if crypto in assets[exchange_name]:
            exchanges.append(exchange)

    return exchanges


async def get_assets():
    assets = {}
    for exchange in EXCHANGE_MAP:
        exchange_name = EXCHANGE_MAP[exchange]
        assets[exchange_name] = await exchange.get_assets()
    return assets


def compute_total_price(offers, required_quantity):
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


def create_initial_response():
    return {
        "coinbase": {"buying_price": None, "selling_price": None},
        "gemini": {"buying_price": None, "selling_price": None},
        "kraken": {"buying_price": None, "selling_price": None},
    }


async def get_sorted_exchange_prices(exchange, crypto, is_buying_price):
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


def sort_prices(prices, reverse=False):
    prices.sort(key=lambda x: x["price"], reverse=reverse)


class FetchAssetsError(Exception):
    pass


class FetchPricesError(Exception):
    pass

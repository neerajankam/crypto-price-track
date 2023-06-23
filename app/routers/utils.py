from exchanges.coinbase import Coinbase
from exchanges.kraken import Kraken
from exchanges.gemini import Gemini
from logger.app_logger import logger


async def get_buying_selling_prices(crypto, quantity):
    exchanges = await get_supported_exchanges(crypto)

    asks = []
    bids = []

    try:
        for exchange in exchanges:
            bids.extend(await exchange.get_bid_price())
            asks.extend(await exchange.get_ask_price())
    except Exception:
        logger.exception("Encountered exception while fetching the bid and ask prices.")
        raise FetchPricesError(
            f"Error while fetching the bid and ask prices of {crypto.value} from exchanges."
        )

    bids.sort(key=lambda x: x["price"], reverse=True)
    asks.sort(key=lambda x: x["price"])

    buying_price = compute_total_price(asks, quantity)
    selling_price = compute_total_price(bids, quantity)
    return buying_price, selling_price


async def get_supported_exchanges(crypto):
    try:
        coinbase_assets = await Coinbase.get_assets()
        gemini_assets = await Gemini.get_assets()
        kraken_assets = await Kraken.get_assets()
    except Exception:
        logger.exception("Encountered exception while fetching supported assets.")
        raise FetchAssetsError(
            "Error while fetching the supported assets from exchanges."
        )
    exchanges = []
    if crypto in coinbase_assets:
        exchanges.append(Coinbase(crypto))
    if crypto in gemini_assets:
        exchanges.append(Gemini(crypto))
    if crypto in kraken_assets:
        exchanges.append(Kraken(crypto))

    return exchanges


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


class FetchAssetsError(Exception):
    pass


class FetchPricesError(Exception):
    pass

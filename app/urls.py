# Base URLs
COINBASE_BASE_URL = "https://api.pro.coinbase.com"
GEMINI_BASE_URL = "https://api.gemini.com/v1"
KRAKEN_BASE_URL = "https://api.kraken.com/0/public"

# URLs to get supported assets
COINBASE_ASSETS_URL = COINBASE_BASE_URL + "/products"
GEMINI_ASSETS_URL = GEMINI_BASE_URL + "/symbols"
KRAKEN_ASSETS_URL = KRAKEN_BASE_URL + "/AssetPairs"

# URLs to get price of supported assets
COINBASE_PRICE_URL = COINBASE_ASSETS_URL + "/{}/book?level=2"
GEMINI_PRICE_URL = GEMINI_BASE_URL + "/book/{}"
KRAKEN_PRICE_URL = KRAKEN_BASE_URL + "/Depth?pair={}"

# URLs to get recent trades
COINBASE_TRADES_URL = COINBASE_ASSETS_URL + "/{}/trades?limit={}"
GEMINI_TRADES_URL = GEMINI_BASE_URL + "/trades/{}?limit_trades={}"
KRAKEN_TRADES_URL = KRAKEN_BASE_URL + "/Trades?pair={}&count={}"

# URLs to get account details
COINBASE_ACCOUNTS_URL = COINBASE_BASE_URL + "/accounts"

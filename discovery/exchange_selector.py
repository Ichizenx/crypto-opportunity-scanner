
import math
import ccxt


# Quote currencies used for market comparison
PREFERRED_QUOTES = ("USDT", "USDC", "USD")

# Representative assets for checking market data quality
REFERENCE_ASSETS = (
    "BTC", "ETH", "BNB", "SOL", "XRP",
    "ADA", "DOGE", "TRX", "TON", "LINK",
    "AVAX", "DOT", "LTC", "BCH", "UNI",
    "NEAR", "APT", "SUI"
)

MAX_TEST_SYMBOLS = 25


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def get_test_symbols(markets):
    """Select representative active Spot markets."""

    symbols = []

    for quote in PREFERRED_QUOTES:
        for base in REFERENCE_ASSETS:
            symbol = f"{base}/{quote}"

            market = markets.get(symbol)

            if (
                market
                and market.get("spot")
                and market.get("active") is not False
            ):
                symbols.append(symbol)

            if len(symbols) >= MAX_TEST_SYMBOLS:
                return symbols

    return symbols


def calculate_liquidity_score(volumes):
    """Score observed quote trading volumes."""

    if not volumes:
        return 0

    average_volume = sum(volumes) / len(volumes)

    if average_volume <= 0:
        return 0

    # Logarithmic score avoids excessive influence from one large market.
    score = (math.log10(average_volume + 1) / 8) * 100

    return round(clamp(score), 2)


def calculate_spread_score(spreads):
    """Score observed bid-ask spreads."""

    if not spreads:
        return 0

    average_spread = sum(spreads) / len(spreads)

    score = 100 - (average_spread * 100)

    return round(clamp(score), 2)


def inspect_exchange(exchange_id):
    """Inspect one exchange using public Spot market data."""

    exchange_class = getattr(ccxt, exchange_id)

    exchange = exchange_class({
        "enableRateLimit": True,
        "timeout": 20000,
        "options": {
            "defaultType": "spot"
        },
    })

    try:
        markets = exchange.load_markets()

        spot_markets = {
            symbol: market
            for symbol, market in markets.items()
            if market.get("spot")
            and market.get("active") is not False
        }

        market_count = len(spot_markets)

        if market_count == 0:
            return None

        symbols = get_test_symbols(spot_markets)

        if not symbols:
            return None

        tickers = {}

        try:
            tickers = exchange.fetch_tickers(symbols)
        except Exception:
            # Fallback for exchanges without batch ticker support.
            for symbol in symbols[:8]:
                try:
                    tickers[symbol] = exchange.fetch_ticker(symbol)
                except Exception:
                    continue

        volumes = []
        spreads = []

        for ticker in tickers.values():

            quote_volume = ticker.get("quoteVolume")

            if quote_volume is not None and quote_volume > 0:
                volumes.append(float(quote_volume))

            bid = ticker.get("bid")
            ask = ticker.get("ask")

            if (
                bid is not None
                and ask is not None
                and bid > 0
                and ask >= bid
            ):
                mid_price = (bid + ask) / 2

                spread_percent = (
                    (ask - bid) / mid_price
                ) * 100

                spreads.append(spread_percent)

        market_coverage_score = clamp(
            (market_count / 500) * 100
        )

        data_quality_score = (
            len(tickers) / len(symbols)
        ) * 100

        liquidity_score = calculate_liquidity_score(volumes)

        spread_score = calculate_spread_score(spreads)

        # Reliability is not assigned an invented score.
        # It requires historical uptime and failure-rate data.
        final_score = (
            liquidity_score * 0.35
            + data_quality_score * 0.30
            + market_coverage_score * 0.20
            + spread_score * 0.15
        )

        return {
            "exchange": exchange_id,
            "score": round(final_score, 2),
            "spot_markets": market_count,
            "liquidity_score": liquidity_score,
            "data_quality_score": round(data_quality_score, 2),
            "market_coverage_score": round(
                market_coverage_score, 2
            ),
            "spread_score": spread_score,
            "tested_symbols": len(symbols),
            "received_tickers": len(tickers),
            "status": "OK",
        }

    finally:
        exchange.close()


def select_top_exchanges():
    """Select exchanges based on observed public market data."""

    candidates = (
        "binance",
        "okx",
        "bybit",
        "kucoin",
        "gateio",
    )

    results = []

    for exchange_id in candidates:

        print(f"\nChecking {exchange_id}...")

        try:
            result = inspect_exchange(exchange_id)

            if result:
                results.append(result)
                print(
                    f"{exchange_id}: "
                    f"Score {result['score']}"
                )
            else:
                print(f"{exchange_id}: No usable Spot data")

        except Exception as error:
            print(f"{exchange_id}: Error - {error}")

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results

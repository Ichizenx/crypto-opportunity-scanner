
import math

from config import (
    CANDIDATE_EXCHANGES,
    EXCHANGE_RANKING,
    MAX_ACTIVE_EXCHANGES,
    MIN_EXCHANGE_QUALITY_SCORE,
    QUOTE_CURRENCIES,
)

from data_sources.exchanges.market_data import MarketDataClient


REFERENCE_ASSETS = (
    "BTC", "ETH", "BNB", "SOL", "XRP",
    "ADA", "DOGE", "TRX", "TON", "LINK",
    "AVAX", "DOT", "LTC", "BCH", "UNI",
    "NEAR", "APT", "SUI",
)

MAX_TEST_SYMBOLS = 25


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def get_test_symbols(markets):
    """Select representative active Spot markets."""

    symbols = []

    for quote in QUOTE_CURRENCIES:
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
    """Calculate preliminary liquidity score."""

    if not volumes:
        return 0

    average_volume = sum(volumes) / len(volumes)

    if average_volume <= 0:
        return 0

    score = (math.log10(average_volume + 1) / 8) * 100

    return round(clamp(score), 2)


def calculate_spread_score(spreads):
    """Calculate score from observed bid-ask spreads."""

    if not spreads:
        return 0

    average_spread = sum(spreads) / len(spreads)
    score = 100 - (average_spread * 100)

    return round(clamp(score), 2)


def calculate_market_coverage_score(
    market_count,
    maximum_market_count,
):
    """Compare exchange coverage with the largest candidate."""

    if maximum_market_count <= 0:
        return 0

    score = (market_count / maximum_market_count) * 100

    return round(clamp(score), 2)


def calculate_data_quality_score(tickers, symbols):
    """Measure completeness of received ticker data."""

    if not symbols:
        return 0

    valid_count = 0

    for symbol in symbols:
        ticker = tickers.get(symbol)

        if not ticker:
            continue

        last = ticker.get("last")
        bid = ticker.get("bid")
        ask = ticker.get("ask")
        quote_volume = ticker.get("quoteVolume")

        if (
            last is not None
            and last > 0
            and bid is not None
            and bid > 0
            and ask is not None
            and ask >= bid
            and quote_volume is not None
            and quote_volume >= 0
        ):
            valid_count += 1

    return round((valid_count / len(symbols)) * 100, 2)


def calculate_final_score(
    liquidity_score,
    data_quality_score,
    market_coverage_score,
    spread_score,
):
    """Calculate weighted exchange score from config."""

    weights = EXCHANGE_RANKING
    total_weight = sum(weights.values())

    if total_weight <= 0:
        return 0

    score = (
        liquidity_score * weights.get("liquidity", 0)
        + data_quality_score * weights.get("data_quality", 0)
        + market_coverage_score * weights.get("market_coverage", 0)
        + spread_score * weights.get("spread", 0)
    ) / total_weight

    return round(clamp(score), 2)


def inspect_exchange(exchange_id):
    """Inspect public Spot market data through shared client."""

    with MarketDataClient(exchange_id) as client:

        markets = client.load_spot_markets()

        market_count = len(markets)

        if market_count == 0:
            return None

        symbols = get_test_symbols(markets)

        if not symbols:
            return None

        tickers = client.get_tickers(
            symbols,
            fallback_limit=8,
        )

        if client.last_ticker_errors:
            print(
                f"{exchange_id}: "
                f"{len(client.last_ticker_errors)} "
                "ticker request error(s)"
            )

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
                mid_price = (ask + bid) / 2

                if mid_price > 0:
                    spread_percent = (
                        (ask - bid) / mid_price
                    ) * 100

                    spreads.append(spread_percent)

        data_quality_score = calculate_data_quality_score(
            tickers,
            symbols,
        )

        liquidity_score = calculate_liquidity_score(volumes)

        spread_score = calculate_spread_score(spreads)

        return {
            "exchange": exchange_id,
            "score": 0,
            "spot_markets": market_count,
            "liquidity_score": liquidity_score,
            "data_quality_score": data_quality_score,
            "market_coverage_score": 0,
            "spread_score": spread_score,
            "tested_symbols": len(symbols),
            "received_tickers": len(tickers),
            "status": "OK",
        }


def select_top_exchanges():
    """Select exchanges using shared client and live market data."""

    results = []

    for exchange_id in CANDIDATE_EXCHANGES:

        print(f"\nChecking {exchange_id}...")

        try:
            result = inspect_exchange(exchange_id)

            if result:
                results.append(result)

                print(
                    f"{exchange_id}: "
                    "Market data received"
                )
            else:
                print(
                    f"{exchange_id}: "
                    "No usable Spot data"
                )

        except Exception as error:
            print(f"{exchange_id}: Error - {error}")

    if not results:
        return []

    maximum_market_count = max(
        item["spot_markets"] for item in results
    )

    for item in results:

        item["market_coverage_score"] = (
            calculate_market_coverage_score(
                item["spot_markets"],
                maximum_market_count,
            )
        )

        item["score"] = calculate_final_score(
            item["liquidity_score"],
            item["data_quality_score"],
            item["market_coverage_score"],
            item["spread_score"],
        )

        if item["score"] < MIN_EXCHANGE_QUALITY_SCORE:
            item["status"] = "BELOW_THRESHOLD"

    results = [
        item for item in results
        if item["score"] >= MIN_EXCHANGE_QUALITY_SCORE
    ]

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:MAX_ACTIVE_EXCHANGES]

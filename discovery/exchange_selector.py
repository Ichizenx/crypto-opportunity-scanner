
import ccxt

from config import (
    CANDIDATE_EXCHANGES,
    EXCHANGE_RANKING,
    MIN_EXCHANGE_QUALITY_SCORE,
    MAX_ACTIVE_EXCHANGES,
)


def evaluate_exchange(exchange_id):
    """Evaluate public Spot market data quality."""

    try:
        exchange_class = getattr(ccxt, exchange_id)

        exchange = exchange_class({
            "enableRateLimit": True,
            "timeout": 15000,
            "options": {
                "defaultType": "spot"
            },
        })

        markets = exchange.load_markets()

        spot_markets = [
            market for market in markets.values()
            if market.get("spot") and market.get("active")
        ]

        if not spot_markets:
            return None

        # Check ticker access on a liquid Spot market.
        symbols = [
            market["symbol"] for market in spot_markets
            if market["quote"] == "USDT"
        ]

        if not symbols:
            return None

        ticker = exchange.fetch_ticker(symbols[0])

        data_quality = 100 if ticker.get("last") else 0
        market_coverage = min(100, len(spot_markets) / 10)

        # These values are provisional until deeper
        # liquidity and reliability measurements are added.
        reliability = 70
        liquidity = 50

        weights = EXCHANGE_RANKING

        score = (
            reliability * weights["reliability"]
            + liquidity * weights["liquidity"]
            + data_quality * weights["data_quality"]
            + market_coverage * weights["market_coverage"]
        ) / 100

        return {
            "exchange": exchange_id,
            "score": round(score, 2),
            "spot_markets": len(spot_markets),
            "data_quality": data_quality,
        }

    except Exception as error:
        print(f"{exchange_id}: unavailable - {error}")
        return None


def select_top_exchanges():
    """Select exchanges that pass the initial quality filter."""

    results = []

    for exchange_id in CANDIDATE_EXCHANGES:
        print(f"Checking {exchange_id}...")

        result = evaluate_exchange(exchange_id)

        if result:
            if result["score"] >= MIN_EXCHANGE_QUALITY_SCORE:
                results.append(result)

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:MAX_ACTIVE_EXCHANGES]


if __name__ == "__main__":
    selected = select_top_exchanges()

    print("\nSelected Spot exchanges:")

    for item in selected:
        print(item)

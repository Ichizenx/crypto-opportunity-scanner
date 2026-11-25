
import sys

from config import (
    PROJECT_NAME,
    VERSION,
    MARKET_TYPE,
    RUNTIME_ENVIRONMENT,
    EXCHANGE_SELECTION_MODE,
    CANDIDATE_EXCHANGES,
    VOLUME_FILTER_MODE,
    MAX_FINAL_CANDIDATES,
    ENABLE_AUTOMATIC_TRADING,
    MIN_SUCCESSFUL_EXCHANGES,
)

from discovery.exchange_selector import select_top_exchanges


def show_project_status():
    print("=" * 55)
    print(PROJECT_NAME)
    print("Version:", VERSION)
    print("Environment:", RUNTIME_ENVIRONMENT)
    print("=" * 55)

    print("Market:", MARKET_TYPE)
    print("Exchange mode:", EXCHANGE_SELECTION_MODE)
    print("Candidate exchanges:", ", ".join(CANDIDATE_EXCHANGES))
    print("Volume filter:", VOLUME_FILTER_MODE)
    print("Maximum candidates:", MAX_FINAL_CANDIDATES)
    print("Minimum successful exchanges:", MIN_SUCCESSFUL_EXCHANGES)
    print("Automatic trading:", ENABLE_AUTOMATIC_TRADING)
    print("=" * 55)


def show_exchange_results(results):
    print("\n" + "=" * 55)
    print("SPOT EXCHANGE QUALITY REPORT")
    print("=" * 55)

    if not results:
        print("No exchange returned usable market data.")
        return

    for rank, item in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print("Exchange:", item["exchange"])
        print("Final score:", item["score"])
        print("Active Spot markets:", item["spot_markets"])
        print("Liquidity score:", item["liquidity_score"])
        print("Data quality:", item["data_quality_score"])
        print("Market coverage:", item["market_coverage_score"])
        print("Spread score:", item["spread_score"])
        print("Tested symbols:", item["tested_symbols"])
        print("Received tickers:", item["received_tickers"])
        print("Status:", item["status"])
        print("-" * 55)


def run_scanner():
    show_project_status()

    print("\nChecking Spot exchanges using public market data...")

    try:
        selected = select_top_exchanges()
        show_exchange_results(selected)

        if len(selected) < MIN_SUCCESSFUL_EXCHANGES:
            print("\nERROR: Not enough successful exchanges.")
            print(
                "Required:",
                MIN_SUCCESSFUL_EXCHANGES,
                "| Available:",
                len(selected),
            )
            return 1

        print("\nExchange selection completed.")
        print("Successful exchanges:", len(selected))
        print("No automatic trades were placed.")

        return 0

    except Exception as error:
        print("\nScanner error:", error)
        return 1


if __name__ == "__main__":
    sys.exit(run_scanner())

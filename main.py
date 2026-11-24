
from config import (
    PROJECT_NAME,
    VERSION,
    MARKET_TYPE,
    EXCHANGE_SELECTION_MODE,
    CANDIDATE_EXCHANGES,
    VOLUME_FILTER_MODE,
    MAX_FINAL_CANDIDATES,
    ENABLE_AUTOMATIC_TRADING,
)

from discovery.exchange_selector import select_top_exchanges


def show_project_status():
    print("=" * 50)
    print(PROJECT_NAME)
    print("Version:", VERSION)
    print("=" * 50)

    print("Market:", MARKET_TYPE)
    print("Exchange mode:", EXCHANGE_SELECTION_MODE)
    print("Candidate exchanges:", ", ".join(CANDIDATE_EXCHANGES))
    print("Volume filter:", VOLUME_FILTER_MODE)
    print("Maximum candidates:", MAX_FINAL_CANDIDATES)
    print("Automatic trading:", ENABLE_AUTOMATIC_TRADING)
    print("=" * 50)


def run_scanner():
    show_project_status()

    print("\nChecking Spot exchanges...")

    try:
        selected = select_top_exchanges()

        if not selected:
            print("No exchange passed the initial quality filter.")
            return

        print("\nSelected exchanges:")

        for item in selected:
            print(
                item["exchange"],
                "| Score:", item["score"],
                "| Spot markets:", item["spot_markets"]
            )

    except Exception as error:
        print("Scanner error:", error)


if __name__ == "__main__":
    run_scanner()


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
    print("Configuration loaded successfully.")


if __name__ == "__main__":
    show_project_status()

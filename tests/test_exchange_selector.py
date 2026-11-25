
from unittest.mock import MagicMock, patch

from discovery import exchange_selector


def test_get_test_symbols():
    markets = {
        "BTC/USDT": {
            "spot": True,
            "active": True,
        },
        "ETH/USDT": {
            "spot": True,
            "active": True,
        },
        "SOL/USDT": {
            "spot": False,
            "active": True,
        },
        "XRP/USDT": {
            "spot": True,
            "active": False,
        },
    }

    symbols = exchange_selector.get_test_symbols(markets)

    assert symbols == ["BTC/USDT", "ETH/USDT"]


def test_inspect_exchange_uses_shared_client():
    fake_client = MagicMock()
    fake_client.__enter__.return_value = fake_client
    fake_client.__exit__.return_value = False
    fake_client.last_ticker_errors = []

    fake_client.load_spot_markets.return_value = {
        "BTC/USDT": {
            "spot": True,
            "active": True,
        }
    }

    fake_client.get_tickers.return_value = {
        "BTC/USDT": {
            "last": 50000,
            "bid": 49990,
            "ask": 50010,
            "quoteVolume": 5000000,
        }
    }

    with patch.object(
        exchange_selector,
        "MarketDataClient",
        return_value=fake_client,
    ) as client_class:

        result = exchange_selector.inspect_exchange("okx")

    client_class.assert_called_once_with("okx")
    fake_client.load_spot_markets.assert_called_once()

    fake_client.get_tickers.assert_called_once()

    assert result["exchange"] == "okx"
    assert result["spot_markets"] == 1
    assert result["received_tickers"] == 1
    assert result["data_quality_score"] == 100


def test_select_top_exchanges_ranks_by_score():
    exchange_a = {
        "exchange": "okx",
        "score": 0,
        "spot_markets": 200,
        "liquidity_score": 90,
        "data_quality_score": 100,
        "market_coverage_score": 0,
        "spread_score": 95,
        "tested_symbols": 25,
        "received_tickers": 25,
        "status": "OK",
    }

    exchange_b = {
        "exchange": "kucoin",
        "score": 0,
        "spot_markets": 100,
        "liquidity_score": 70,
        "data_quality_score": 90,
        "market_coverage_score": 0,
        "spread_score": 85,
        "tested_symbols": 25,
        "received_tickers": 25,
        "status": "OK",
    }

    with (
        patch.object(
            exchange_selector,
            "CANDIDATE_EXCHANGES",
            ["okx", "kucoin"],
        ),
        patch.object(
            exchange_selector,
            "MIN_EXCHANGE_QUALITY_SCORE",
            0,
        ),
        patch.object(
            exchange_selector,
            "inspect_exchange",
            side_effect=[exchange_a, exchange_b],
        ),
    ):
        results = exchange_selector.select_top_exchanges()

    assert len(results) == 2
    assert results[0]["exchange"] == "okx"
    assert results[1]["exchange"] == "kucoin"
    assert results[0]["score"] > results[1]["score"]

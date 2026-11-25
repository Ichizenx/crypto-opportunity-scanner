
from unittest.mock import MagicMock, patch

import ccxt
import pytest

from data_sources.exchanges.market_data import MarketDataClient


def create_client():
    """Create a client with a mocked exchange."""

    fake_exchange = MagicMock()

    with patch.object(
        ccxt,
        "okx",
        return_value=fake_exchange,
    ):
        client = MarketDataClient("okx")

    return client, fake_exchange


def test_reject_unsupported_exchange():
    with pytest.raises(ValueError):
        MarketDataClient("not_a_real_exchange")


def test_client_initialization():
    client, fake_exchange = create_client()

    assert client.exchange_id == "okx"
    assert client.closed is False

    client.close()


def test_load_spot_markets():
    client, fake_exchange = create_client()

    fake_exchange.load_markets.return_value = {
        "BTC/USDT": {
            "spot": True,
            "active": True,
        },
        "ETH/USDT": {
            "spot": True,
            "active": False,
        },
        "BTC/USD:USD": {
            "spot": False,
            "active": True,
        },
    }

    markets = client.load_spot_markets()

    assert list(markets.keys()) == ["BTC/USDT"]

    client.close()


def test_get_ticker():
    client, fake_exchange = create_client()

    fake_exchange.fetch_ticker.return_value = {
        "last": 50000,
        "bid": 49990,
        "ask": 50010,
        "baseVolume": 100,
        "quoteVolume": 5000000,
        "percentage": 2.5,
        "timestamp": 123456789,
    }

    ticker = client.get_ticker("BTC/USDT")

    assert ticker["symbol"] == "BTC/USDT"
    assert ticker["last_price"] == 50000
    assert ticker["quote_volume"] == 5000000
    assert ticker["change_percent"] == 2.5

    client.close()


def test_get_tickers_batch():
    client, fake_exchange = create_client()

    fake_exchange.fetch_tickers.return_value = {
        "BTC/USDT": {"last": 50000},
        "ETH/USDT": {"last": 3000},
    }

    tickers = client.get_tickers(
        ["BTC/USDT", "ETH/USDT"]
    )

    assert len(tickers) == 2
    fake_exchange.fetch_ticker.assert_not_called()

    client.close()


def test_get_tickers_fallback():
    client, fake_exchange = create_client()

    fake_exchange.fetch_tickers.side_effect = Exception(
        "Batch request failed"
    )

    fake_exchange.fetch_ticker.return_value = {
        "last": 50000
    }

    tickers = client.get_tickers(
        ["BTC/USDT", "ETH/USDT"],
        fallback_limit=1,
    )

    assert "BTC/USDT" in tickers
    assert len(client.last_ticker_errors) == 1
    fake_exchange.fetch_ticker.assert_called_once_with(
        "BTC/USDT"
    )

    client.close()


def test_close_is_safe():
    client, fake_exchange = create_client()

    client.close()
    client.close()

    assert client.closed is True
    fake_exchange.close.assert_called_once()


def test_requests_after_close_are_rejected():
    client, fake_exchange = create_client()

    client.close()

    with pytest.raises(RuntimeError):
        client.load_spot_markets()

    fake_exchange.load_markets.assert_not_called()


def test_context_manager_closes_connection():
    client, fake_exchange = create_client()

    with client as active_client:
        assert active_client is client
        assert client.closed is False

    assert client.closed is True
    fake_exchange.close.assert_called_once()


def test_invalid_ohlcv_limit():
    client, fake_exchange = create_client()

    with pytest.raises(ValueError):
        client.get_ohlcv("BTC/USDT", limit=0)

    fake_exchange.fetch_ohlcv.assert_not_called()

    client.close()


def test_invalid_order_book_limit():
    client, fake_exchange = create_client()

    with pytest.raises(ValueError):
        client.get_order_book("BTC/USDT", limit=0)

    fake_exchange.fetch_order_book.assert_not_called()

    client.close()

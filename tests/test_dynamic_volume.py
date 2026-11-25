
import pytest

from filters.dynamic_volume import (
    calculate_relative_volume,
    check_spread,
    check_order_book_depth,
    evaluate_volume,
)

from discovery.exchange_selector import (
    calculate_market_coverage_score,
    calculate_data_quality_score,
    calculate_final_score,
)


# ==========================================
# DYNAMIC VOLUME TESTS
# ==========================================

def test_relative_volume():
    result = calculate_relative_volume(300, [100, 100, 100])
    assert result == 3.0


def test_relative_volume_without_history():
    result = calculate_relative_volume(300, [])
    assert result is None


def test_spread_acceptable():
    assert check_spread(99.9, 100) is True


def test_spread_too_wide():
    assert check_spread(99, 101) is False


def test_order_book_depth():
    order_book = {
        "bids": [[100, 2], [99, 3]],
        "asks": [[101, 2], [102, 3]],
    }

    assert check_order_book_depth(order_book) is True


def test_empty_order_book():
    assert check_order_book_depth({}) is False


def test_evaluate_volume_pass():
    order_book = {
        "bids": [[100, 2]],
        "asks": [[100.1, 2]],
    }

    result = evaluate_volume(
        current_volume=300,
        historical_volumes=[100, 100, 100],
        bid=100,
        ask=100.1,
        order_book=order_book,
    )

    assert result["status"] == "PASS"


# ==========================================
# EXCHANGE SELECTOR TESTS
# ==========================================

def test_market_coverage_score():
    assert calculate_market_coverage_score(1000, 2000) == 50.0


def test_market_coverage_best_exchange():
    assert calculate_market_coverage_score(2000, 2000) == 100.0


def test_market_coverage_without_reference():
    assert calculate_market_coverage_score(1000, 0) == 0


def test_data_quality_complete():
    symbols = ["BTC/USDT", "ETH/USDT"]

    tickers = {
        "BTC/USDT": {
            "last": 100,
            "bid": 99,
            "ask": 101,
            "quoteVolume": 100000,
        },
        "ETH/USDT": {
            "last": 200,
            "bid": 199,
            "ask": 201,
            "quoteVolume": 50000,
        },
    }

    assert calculate_data_quality_score(tickers, symbols) == 100.0


def test_data_quality_incomplete():
    symbols = ["BTC/USDT", "ETH/USDT"]

    tickers = {
        "BTC/USDT": {
            "last": 100,
            "bid": 99,
            "ask": 101,
            "quoteVolume": 100000,
        },
        "ETH/USDT": {
            "last": 200,
            "bid": None,
            "ask": 201,
            "quoteVolume": 50000,
        },
    }

    assert calculate_data_quality_score(tickers, symbols) == 50.0


def test_final_score_uses_weights():
    result = calculate_final_score(
        liquidity_score=100,
        data_quality_score=100,
        market_coverage_score=100,
        spread_score=100,
    )

    assert result == 100.0


def test_final_score_zero():
    result = calculate_final_score(0, 0, 0, 0)

    assert result == 0.0

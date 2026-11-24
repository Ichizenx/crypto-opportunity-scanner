
from filters.dynamic_volume import (
    calculate_relative_volume,
    check_spread,
    check_order_book_depth,
    evaluate_volume,
)


def test_relative_volume():
    result = calculate_relative_volume(
        300,
        [100, 100, 100]
    )
    assert result == 3.0


def test_relative_volume_without_history():
    result = calculate_relative_volume(300, [])
    assert result is None


def test_spread_is_acceptable():
    assert check_spread(99.8, 100.2) is True


def test_spread_is_too_wide():
    assert check_spread(98, 102) is False


def test_order_book_depth():
    order_book = {
        "bids": [[100, 5]],
        "asks": [[101, 5]]
    }

    assert check_order_book_depth(order_book) is True


def test_empty_order_book():
    assert check_order_book_depth({}) is False


def test_evaluate_volume_pass():
    order_book = {
        "bids": [[100, 5]],
        "asks": [[101, 5]]
    }

    result = evaluate_volume(
        current_volume=300,
        historical_volumes=[100, 100, 100],
        bid=99.9,
        ask=100.1,
        order_book=order_book
    )

    assert result["status"] == "PASS"

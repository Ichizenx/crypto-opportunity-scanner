
from statistics import mean


def calculate_relative_volume(current_volume, historical_volumes):
    """
    Compare current volume with historical average volume.
    """

    if not historical_volumes:
        return None

    average_volume = mean(historical_volumes)

    if average_volume <= 0:
        return None

    return round(current_volume / average_volume, 2)


def check_spread(bid, ask, max_spread_percent=0.50):
    """
    Calculate bid-ask spread percentage.
    """

    if bid is None or ask is None or bid <= 0 or ask <= 0:
        return False

    mid_price = (bid + ask) / 2

    spread_percent = ((ask - bid) / mid_price) * 100

    return spread_percent <= max_spread_percent


def check_order_book_depth(order_book, minimum_depth=0):
    """
    Estimate order book depth using available bids and asks.
    """

    if not order_book:
        return False

    bids = order_book.get("bids", [])
    asks = order_book.get("asks", [])

    if not bids or not asks:
        return False

    bid_depth = sum(price * amount for price, amount in bids)
    ask_depth = sum(price * amount for price, amount in asks)

    total_depth = bid_depth + ask_depth

    return total_depth >= minimum_depth


def evaluate_volume(
    current_volume,
    historical_volumes,
    bid,
    ask,
    order_book,
    relative_volume_min=1.5,
    max_spread_percent=0.50,
):
    """
    Evaluate volume and liquidity conditions.
    """

    relative_volume = calculate_relative_volume(
        current_volume,
        historical_volumes
    )

    spread_ok = check_spread(
        bid,
        ask,
        max_spread_percent
    )

    depth_ok = check_order_book_depth(order_book)

    if relative_volume is None:
        status = "INSUFFICIENT_DATA"

    elif (
        relative_volume >= relative_volume_min
        and spread_ok
        and depth_ok
    ):
        status = "PASS"

    else:
        status = "REJECT"

    return {
        "relative_volume": relative_volume,
        "spread_ok": spread_ok,
        "depth_ok": depth_ok,
        "status": status,
    }

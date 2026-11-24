
import ccxt


class MarketDataClient:
    """
    Fetch public Spot market data from cryptocurrency exchanges.
    """

    def __init__(self, exchange_id):
        exchange_class = getattr(ccxt, exchange_id)

        self.exchange = exchange_class({
            "enableRateLimit": True,
            "timeout": 20000,
            "options": {
                "defaultType": "spot"
            },
        })

    def load_spot_markets(self):
        """Return active Spot markets."""

        markets = self.exchange.load_markets()

        return {
            symbol: market
            for symbol, market in markets.items()
            if market.get("spot") and market.get("active") is not False
        }

    def get_ticker(self, symbol):
        """Get latest price and 24-hour volume."""

        ticker = self.exchange.fetch_ticker(symbol)

        return {
            "symbol": symbol,
            "last_price": ticker.get("last"),
            "bid": ticker.get("bid"),
            "ask": ticker.get("ask"),
            "base_volume": ticker.get("baseVolume"),
            "quote_volume": ticker.get("quoteVolume"),
            "change_percent": ticker.get("percentage"),
        }

    def get_ohlcv(self, symbol, timeframe="1h", limit=100):
        """Get historical candles."""

        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=limit
        )

        return [
            {
                "timestamp": candle[0],
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5],
            }
            for candle in candles
        ]

    def get_order_book(self, symbol, limit=20):
        """Get current order book."""

        return self.exchange.fetch_order_book(
            symbol,
            limit=limit
        )

    def close(self):
        self.exchange.close()

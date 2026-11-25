
import ccxt


class MarketDataClient:
    """
    Shared public Spot market data client.

    Compatible with Windows and Android Termux.
    Uses CCXT and public exchange market data only.
    """

    def __init__(self, exchange_id, timeout=20000):
        exchange_id = str(exchange_id).strip().lower()

        if exchange_id not in ccxt.exchanges:
            raise ValueError(
                f"Unsupported exchange: {exchange_id}"
            )

        if timeout <= 0:
            raise ValueError("Timeout must be positive.")

        exchange_class = getattr(ccxt, exchange_id)

        self.exchange_id = exchange_id
        self.closed = False
        self.last_ticker_errors = []

        self.exchange = exchange_class({
            "enableRateLimit": True,
            "timeout": timeout,
            "options": {
                "defaultType": "spot",
            },
        })

    def _ensure_open(self):
        """Prevent requests after the client has been closed."""

        if self.closed:
            raise RuntimeError(
                f"Exchange client '{self.exchange_id}' is closed."
            )

    def load_spot_markets(self):
        """Return active Spot markets."""

        self._ensure_open()

        markets = self.exchange.load_markets()

        return {
            symbol: market
            for symbol, market in markets.items()
            if market.get("spot")
            and market.get("active") is not False
        }

    def get_ticker(self, symbol):
        """Get normalized ticker information for one symbol."""

        self._ensure_open()

        if not symbol:
            raise ValueError("Symbol cannot be empty.")

        ticker = self.exchange.fetch_ticker(symbol)

        return {
            "symbol": symbol,
            "last_price": ticker.get("last"),
            "bid": ticker.get("bid"),
            "ask": ticker.get("ask"),
            "base_volume": ticker.get("baseVolume"),
            "quote_volume": ticker.get("quoteVolume"),
            "change_percent": ticker.get("percentage"),
            "timestamp": ticker.get("timestamp"),
        }

    def get_tickers(self, symbols=None, fallback_limit=8):
        """
        Fetch multiple tickers.

        If batch fetching fails, try individual requests
        for a limited number of symbols.
        """

        self._ensure_open()

        self.last_ticker_errors = []

        if symbols is not None:
            symbols = list(symbols)

            if not symbols:
                return {}

        if fallback_limit < 0:
            raise ValueError(
                "Fallback limit cannot be negative."
            )

        try:
            tickers = self.exchange.fetch_tickers(symbols)

            if tickers:
                return tickers

        except Exception as error:
            self.last_ticker_errors.append({
                "operation": "fetch_tickers",
                "error": str(error),
            })

        if not symbols or fallback_limit == 0:
            return {}

        tickers = {}

        for symbol in symbols[:fallback_limit]:
            try:
                tickers[symbol] = self.exchange.fetch_ticker(
                    symbol
                )

            except Exception as error:
                self.last_ticker_errors.append({
                    "operation": "fetch_ticker",
                    "symbol": symbol,
                    "error": str(error),
                })

        return tickers

    def get_ohlcv(self, symbol, timeframe="1h", limit=100):
        """Get historical OHLCV candles."""

        self._ensure_open()

        if not symbol:
            raise ValueError("Symbol cannot be empty.")

        if limit <= 0:
            raise ValueError("Candle limit must be positive.")

        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=limit,
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
            if candle and len(candle) >= 6
        ]

    def get_order_book(self, symbol, limit=20):
        """Get the current order book."""

        self._ensure_open()

        if not symbol:
            raise ValueError("Symbol cannot be empty.")

        if limit <= 0:
            raise ValueError(
                "Order book limit must be positive."
            )

        return self.exchange.fetch_order_book(
            symbol,
            limit=limit,
        )

    def close(self):
        """Close the exchange connection safely."""

        if self.closed:
            return

        self.closed = True

        try:
            self.exchange.close()

        except Exception as error:
            print(
                f"Warning: Could not close "
                f"{self.exchange_id}: {error}"
            )

    def __enter__(self):
        self._ensure_open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False


import os

# ==========================================
# CRYPTO OPPORTUNITY SCANNER
# Central Configuration
# ==========================================

PROJECT_NAME = "Crypto Opportunity Scanner"
VERSION = "0.2.0"

# ------------------------------------------
# RUNTIME ENVIRONMENT
# ------------------------------------------

RUNTIME_ENVIRONMENT = os.getenv(
    "SCANNER_ENVIRONMENT",
    "auto"
)

SUPPORTED_ENVIRONMENTS = [
    "github",
    "windows",
    "termux",
]

# ------------------------------------------
# MARKET SETTINGS
# ------------------------------------------

MARKET_TYPE = "spot"
ENABLE_FUTURES = False

QUOTE_CURRENCIES = [
    "USDT",
    "USDC",
    "BTC",
    "FDUSD",
]

# ------------------------------------------
# EXCHANGE DISCOVERY
# ------------------------------------------

EXCHANGE_SELECTION_MODE = "dynamic"

CANDIDATE_EXCHANGES = [
    "okx",
    "kucoin",
    "gate",
    "binance",
    "bybit",
]

EXCHANGE_RANKING = {
    "liquidity": 35,
    "data_quality": 30,
    "market_coverage": 20,
    "spread": 15,
}

MIN_EXCHANGE_QUALITY_SCORE = 70
MAX_ACTIVE_EXCHANGES = 5

# Minimum successful exchanges required
MIN_SUCCESSFUL_EXCHANGES = 1

# ------------------------------------------
# DATA SOURCES
# ------------------------------------------

CMC_API_KEY = os.getenv("CMC_API_KEY", "")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

USE_COINMARKETCAP = True
USE_COINGECKO = True

# ------------------------------------------
# DYNAMIC VOLUME FILTER
# ------------------------------------------

VOLUME_FILTER_MODE = "dynamic"

VOLUME_LOOKBACK_PERIODS = 30
RELATIVE_VOLUME_MIN = 1.5

CHECK_ORDER_BOOK_DEPTH = True
CHECK_SPREAD = True
CHECK_VOLUME_STABILITY = True
CHECK_ABNORMAL_VOLUME = True

MAX_SPREAD_PERCENT = 0.50

# ------------------------------------------
# TECHNICAL ANALYSIS
# ------------------------------------------

TIMEFRAMES = [
    "15m",
    "1h",
    "4h",
    "1d",
]

ENABLE_ICHIMOKU = True
ENABLE_ICT = True
ENABLE_RTM = True
ENABLE_MARKET_STRUCTURE = True
ENABLE_LIQUIDITY_ANALYSIS = True

ENABLE_RSI = True
ENABLE_MACD = True

# ------------------------------------------
# FUNDAMENTAL ANALYSIS
# ------------------------------------------

ENABLE_FUNDAMENTAL_ANALYSIS = True
CHECK_TOKENOMICS = True
CHECK_TOKEN_UNLOCKS = True
CHECK_CIRCULATING_SUPPLY = True
CHECK_PROJECT_ACTIVITY = True
CHECK_PROJECT_NEWS = True

# ------------------------------------------
# ON-CHAIN ANALYSIS
# ------------------------------------------

ENABLE_ONCHAIN_ANALYSIS = True
ENABLE_WHALE_TRACKING = True
ENABLE_SMART_MONEY = True
ENABLE_EXCHANGE_FLOWS = True
ENABLE_UNUSUAL_TRANSFERS = True

UNKNOWN_DATA_IS_NEUTRAL = True

# ------------------------------------------
# OPPORTUNITY SCORING
# ------------------------------------------

SCORING_WEIGHTS = {
    "technical": 30,
    "liquidity": 25,
    "onchain": 20,
    "fundamental": 15,
    "market_quality": 10,
}

MAX_FINAL_CANDIDATES = 10
MAX_DEEP_ANALYSIS = 3

SIGNAL_STATUSES = [
    "BUY",
    "SELL",
    "WAIT",
    "AVOID",
]

# ------------------------------------------
# RISK SETTINGS
# ------------------------------------------

RISK_LEVEL = "moderate"
ANALYSIS_HORIZON_DAYS = [3, 30]

ENABLE_AUTOMATIC_TRADING = False

# ------------------------------------------
# REPORT SETTINGS
# ------------------------------------------

REPORT_TIMEZONE = "Asia/Tehran"
REPORT_HOUR = 8
REPORT_MINUTE = 0

ENABLE_DAILY_REPORT = True
ENABLE_TELEGRAM_ALERTS = True

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ------------------------------------------
# STORAGE AND API SAFETY
# ------------------------------------------

DATA_DIRECTORY = "data"
CACHE_DIRECTORY = "cache"

REQUEST_TIMEOUT_SECONDS = 20
MAX_RETRIES = 3
API_REQUEST_DELAY_SECONDS = 1

SAVE_REPORTS = True
SAVE_MARKET_DATA = True

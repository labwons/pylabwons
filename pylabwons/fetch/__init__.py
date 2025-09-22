from .stock.tickers import (
    get_sectors,
    get_foreigner_rates,
    get_market_caps,
    get_corporations,
    get_ohlcvs,
    get_multiples
)

from .stock.series import (
    get_ohlcv,
    get_market_cap,
    get_foreigner_rate,
    backfill
)


# Alias
ohlcvs = get_ohlcvs
sectors = get_sectors
foreigner_rates = get_foreigner_rates
market_caps = get_market_caps
corporations = get_corporations
multiples = get_multiples

ohlcv = get_ohlcv
market_cap = get_market_cap
foreigner_rate = get_foreigner_rate
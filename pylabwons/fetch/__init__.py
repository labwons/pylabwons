from .stock.tickers import (
    get_sectors,
    get_foreigner_rates,
    get_market_caps,
    get_corporations,
    get_ohlcvs
)

from .stock.series import (
    get_ohlcv,
    get_foreigner_rate
)


# Alias
ohlcvs = get_ohlcvs
sectors = get_sectors
foreigner_rates = get_foreigner_rates
market_caps = get_market_caps
corporations = get_corporations

ohlcv = get_ohlcv
foreigner_rate = get_foreigner_rate
__all__ = [
    "backtest_return",
    "bollinger_band",
    "bollinger_band_squeeze_and_expand",
    "simple_ma",
    "typical_price",
]

from pandas import DataFrame, Series
import pandas as pd


def backtest_return(ohlc:DataFrame, *forward_days, **kwargs) -> DataFrame:
    price = ohlc[kwargs['by'] if 'by' in kwargs else 'close']
    for days in forward_days:
        w = int(days / 5)
        m = int(days / 20)
        y = int(m / 12)
        if days < 20 and w:
            name = f'forward{w}wReturn'
        else:
            name = f'forward{y}yReturn' if y else f'forward{m}mReturn'
        ohlc[name] = round(100 * (price.shift(-days) / price - 1), 2)
    return ohlc

def typical_price(ohlc:DataFrame) -> DataFrame:
    ohlc['typical'] = (ohlc.close + ohlc.high + ohlc.low) / 3
    return ohlc

def simple_ma(ohlct:DataFrame, *days) -> DataFrame:
    if not days:
        days = [5, 20, 60, 120, 200]
    for day in days:
        ohlct[f'MA{day}D'] = ohlct.typical.rolling(day).mean()
    return ohlct

def bollinger_band(ohlct:DataFrame, window:int=20, window_dev:int=2) -> DataFrame:
    rolling = ohlct.typical.rolling(window)
    half_dev = int(window_dev / 2)
    ohlct['bollinger_mid'] = mid = rolling.mean()
    ohlct[f'bollinger_upper_{window_dev}x'] = upper = mid + window_dev * rolling.std()
    ohlct[f'bollinger_lower_{window_dev}x'] = lower = mid - window_dev * rolling.std()
    ohlct[f'bollinger_upper_{half_dev}x'] = mid + half_dev * rolling.std()
    ohlct[f'bollinger_lower_{half_dev}x'] = mid - half_dev * rolling.std()
    ohlct['bollinger_width'] = width = ((upper - lower) / mid) * 100
    return ohlct

def bollinger_band_squeeze_and_expand(ta:DataFrame, window:int=252, squeeze_pct:float=0.1) -> DataFrame:
    """
    단독 사용은 적합하지 않음
    - runtime: parameter에 따라 상이하나, 5분 가까이 소요됨
    - 주요 결과 예시(1) window=126 / squeeze_pct=0.2 적용 시
    	    forward2wReturn	forward1mReturn	forward2mReturn	forward3mReturn	forward6mReturn
    count	          48765	          48264	          47978	          47431	          45943
    mean	       0.355926	       0.596561	       1.488299	       2.244687	       5.151853
    std	          10.421582	      14.896541	      22.347626	       7.989898	      43.100466
    min	         -80.620000	     -83.420000	     -87.080000	     -88.150000	     -89.900000
    25%	          -4.690000	      -6.960000	      -9.850000	     -12.170000	     -16.565000
    50%	          -0.560000	      -1.065000	      -1.465000	      -1.750000	      -2.780000
    75%	           3.730000	       5.660000	       8.450000	      10.410000	      15.360000
    max	         355.100000	     430.150000	     637.860000	     965.310000	    1483.820000
    pos	              21953	          21527	          21535	          21393	          20497
    neg	              26072	          26288	          26151	          25791	          25275
    pos%	      45.017943	      44.602602	      44.885156	      45.103413	      44.613978
    > 5%	      20.317851	      26.796370	      31.758306	      34.066328	      36.958840
    > 8%	      12.765303	      19.397481	      25.755555	      28.652147	      32.960407
    > 10%	       9.461704	      15.715647	      22.299804	      25.565558	      30.418127
    > 12%	       7.367989	      13.088430	      19.379716	      22.831060	      28.193631

    - 주요 결과 예시(2) window=252 / squeeze_pct=0.05 적용 시
            forward2wReturn	forward1mReturn	forward2mReturn	forward3mReturn	forward6mReturn
    count             12813	          12666	          12591	          12389	          11993
    mean	       0.235135	       0.345414	       1.510392	       1.883581	       4.356763
    std	           8.892187	      12.627832	      20.109460	      24.481121	      38.098076
    min	         -54.680000	     -60.110000	     -68.360000	     -80.700000	     -85.030000
    25%	          -4.230000	      -6.390000	      -8.990000	     -11.290000	     -15.930000
    50%	          -0.460000	      -1.030000	      -1.210000	      -1.740000	      -2.860000
    75%	           3.480000	       5.167500	       8.025000	       9.590000	      14.000000
    max	         311.940000	     234.140000	     481.440000	     423.740000	     750.760000
    pos	               5825	           5571	           5703	           5541	           5263
    neg	               6771	           6975	           6798	           6781	           6684
    pos%	      45.461641	      43.983894	      45.294258	      44.725159	      43.883932
    > 5%	      19.183642	      25.430286   	  31.355730	      33.360239	      35.862587
    > 8%	      11.301022	      17.835149	      25.041696	      27.564775	      31.743517
    > 10%          8.233825	      14.171799	      21.594790	      24.416821	      29.208705
    > 12%          6.251463	      11.740092	      18.767374	      21.753168	      27.015759

    :param ta:
    :param window:
    :param squeeze_pct:
    :return:
    """
    ta['_t_rank'] = ta["bollinger_width"].rolling(window).apply(
        lambda x: Series(x).rank(pct=True).iloc[-1]
    )
    ta['bollinger_squeeze_and_expand_long'] = (
        (ta['_t_rank'] < squeeze_pct) &
        (ta['close'] > ta['bollinger_upper_2x']) &
        (ta['volume'] > ta['volume'].rolling(20).mean() * 1.5)
    ).astype(int) * ta['close']
    del ta['_t_rank']
    return ta
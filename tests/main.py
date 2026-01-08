import pylabwons as lw
import pandas as pd
pd.set_option('display.expand_frame_repr', False)


if __name__ == "__main__":

    key = 'KRW-H'
    src = r"E:\SIDEPROJ\labwons-analytic\src\analysis\archive\baseline.parquet"
    data = pd.read_parquet(src, engine='pyarrow')
    unit = data[key].copy()

    # single = lw.Indicator(data[key])
    # single.add_typical_price()
    # single.add_bollinger_band()
    # single.add_macd()
    # print(single)

    # bundle = lw.Indicator(data)
    # bundle.add_typical_price()
    # bundle.add_bollinger_band()
    # bundle.add_macd()
    # print(bundle)

    # single = lw.Detector(data[key])
    # single.detect_rapid_drop('close', window=5, threshold=0.1)
    # print(single)

    # bundle = lw.Detector(data)
    # bundle.detect_rapid_drop('close', window=5, threshold=0.1)
    # print(bundle['sig_rapid_drop'])
    # print(bundle(key))


    # ticker = lw.Ticker(unit)
    # ticker.detect_rapid_drop('close', window=5, threshold=0.1)
    # print(ticker)
    # ticker.view()

    tester = lw.BackTester(data)
    tester.calc_return(5)
    tester.add_bollinger_band('close', window=20, std=2)
    tester.add_macd('close', window_slow=26, window_fast=12, window_sign=9)
    tester.add_average_true_range(window=10)
    tester.add_volume_roc(window=7)
    tester.add_obv_slope(window=12)
    tester.add_rsi(window=9)
    # print(tester)
    print(tester.data.stack(level=0, future_stack=True))
    # tester.detect_rapid_drop('tp', window=5, threshold=0.1)

    # reverse = tester.serialize(5)
    # reverse = reverse[reverse['return5High'] >= 0.04]
    # print(tester)
    # print(reverse)
    # print(tester.report(5, sig_rapid_drop=True))
    # print(tester.report(5))

    # tester.view_gaussian(5)
    # tester.view_indicator(tester['ma20'], row=1, col=1)
    # tester.view_signal('buy', tester['sig_rapid_drop'])
    # tester.view()


    # market = lw.Tickers(data)

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
    tester.detect_rapid_drop('tp', window=5, threshold=0.1)
    tester.calc_return(5)
    tester.view_gaussian('sig_rapid_drop', 5)
    print(tester.report('sig_rapid_drop', 5))

    # tester.view_indicator(tester['ma20'], row=1, col=1)
    # tester.view_signal('buy', tester['sig_rapid_drop'])
    # tester.view()


    # market = lw.Tickers(data)

#!/usr/bin/env python
import datetime as dt
import pandas as pd

start_date = dt.datetime(2020, 1, 1, 0, 0)
end_date = dt.datetime(2020, 12, 31, 0, 0)

df = pd.read_csv("/Volumes/Extreme SSD/datas/hist/USD_JPY/2020.csv", names=('dtime', 'open', 'high', 'low', 'close', 'volume'), dtype={'open': 'double', 'high': 'double', 'low': 'double', 'close': 'double', 'volume':'int'}, parse_dates=['dtime', ], index_col=1)
# df = df.set_index('dtime')

# df1 = read_df("/Volumes/Extreme SSD/datas/hist/USD_JPY/2020.csv", 240)
# df1 = df1.loc[start_date:end_date]
print(df.columns)
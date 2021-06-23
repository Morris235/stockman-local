import pandas as pd
import matplotlib.pyplot as plt
import datetime
import mplfinance as mpf
import matplotlib.dates as mdates
from DB import Analyzer
from mplfinance.original_flavor import candlestick_ohlc


compName = '삼성전자'
mk = Analyzer.MarketDB()
df = mk.get_daily_price(compName,'2020-01-01')

ema60 = df.close.ewm(span=60).mean()  # 종가의 12주 지수 이동평균
ema130 = df.close.ewm(span=130).mean()  # 종가의 26주 지수 이동평균
macd = ema60 - ema130  # MACD선
signal = macd.ewm(span=45).mean()  # 신호선(MACD의 9주 지수 이동평균)
macdhist = macd - signal  # MACD 히스토그램

df = df.assign(ema130=ema130,  ema60=ema60, macd=macd, signal=signal, macdhist=macdhist).dropna()
df['number'] = df.index.map(mdates.date2num)  # 캔들 차트에 사용할 수 있게 날짜(date)형 인덱스를 숫자형으로 변환한다.
ohlc = df[['number', 'open', 'high', 'low', 'close']]

plt.figure(figsize=(9, 7))
p1 = plt.subplot(2, 1, 1)
plt.title('Triple Screen Trading - First Screen')
plt.grid(True)

candlestick_ohlc(p1,ohlc.values, width=.6, colorup='red', colordown='blue')  # ohlc의 숫자형 일자, 시가, 고가, 저가, 종가 값을 이용해서 캔들 차트를 그린다.
p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['ema130'], color='c', label='EMA130')
plt.legend(loc='best')

p2 = plt.subplot(2, 1, 2)
plt.grid(True)
p2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.bar(df.number, df['macdhist'], color='m', label='MACD-Hist')
plt.plot(df.number, df['macd'], color='b', label='MACD')
plt.plot(df.number, df['signal'], 'g--', label='MACD-Signal')
plt.legend(loc='best')
plt.show()

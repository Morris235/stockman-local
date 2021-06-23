import pandas as pd
import matplotlib.pyplot as plt
import datetime
import mplfinance as mpf
import matplotlib.dates as mdates
from DB import Analyzer
from mplfinance.original_flavor import candlestick_ohlc


compName = '엔씨소프트'
mk = Analyzer.MarketDB()
df = mk.get_daily_price(compName, '2020-01-01')

ema60 = df.close.ewm(span=60).mean()  # 종가의 12주 지수 이동평균
ema130 = df.close.ewm(span=130).mean()  # 종가의 26주 지수 이동평균
macd = ema60 - ema130  # MACD선
signal = macd.ewm(span=45).mean()  # 신호선(MACD의 9주 지수 이동평균)
macdhist = macd - signal  # MACD 히스토그램

df = df.assign(ema130=ema130,  ema60=ema60, macd=macd, signal=signal, macdhist=macdhist).dropna()
df['number'] = df.index.map(mdates.date2num)  # 캔들 차트에 사용할 수 있게 날짜(date)형 인덱스를 숫자형으로 변환한다.
ohlc = df[['number', 'open', 'high', 'low', 'close']]

# 14일 동안의 최댓값을 구한다. min_periodos=1을 지정할 경우, 14일 기간에 해당하는 데이터가 모두 누적되지 않았더라도 최소 기간인 1일 이상의 데이터만 존재하면 최댓값을 구하라는 의미다.
ndays_high = df.high.rolling(window=14, min_periods=1).max()
# 14일 동안의 최솟값을 구한다. min_periodos=1로 지정하면, 14일 치 데이터가 모두 누적되지 않았더라도 최소 기간인 1일 이상의 데이터만 존재하면 최솟값을 구하라는 의미다.
ndays_low = df.low.rolling(window=14, min_periods=1).min()
fast_k = (df.close - ndays_low) / (ndays_high - ndays_low) * 100  # 빠른선 %K를 구한다.
slow_d = fast_k.rolling(window=3).mean()  # 3일 동안 %K의 평균을 구해서 느린 선 %D에 저장한다.
df = df.assign(fast_k=fast_k, slow_d=slow_d,).dropna()  # %K와 %D로 데이터프레임을 생성한 뒤 결측치는 제거한다.

plt.figure(figsize=(9, 7))
p1 = plt.subplot(2, 1, 1)
plt.title('Triple Screen Trading - Second Screen')
plt.grid(True)

candlestick_ohlc(p1,ohlc.values, width=.6, colorup='red', colordown='blue')  # ohlc의 숫자형 일자, 시가, 고가, 저가, 종가 값을 이용해서 캔들 차트를 그린다.
p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['ema130'], color='c', label='EMA130')
plt.legend(loc='best')

p1 = plt.subplot(2, 1, 2)
plt.grid(True)
p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['fast_k'], color='c', label='%K')
plt.plot(df.number, df['slow_d'], color='k', label='%D')
plt.yticks([0, 20, 80, 100])  # Y축 눈금을 0, 20, 80, 100으로 설정하여 스토캐스틱의 기준선을 나타낸다.
plt.legend(loc='best')
plt.show()
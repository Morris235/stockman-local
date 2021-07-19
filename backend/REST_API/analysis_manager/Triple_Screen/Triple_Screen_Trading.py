"""
두 번째 창에 일간 오실레이터로 스토캐스틱의 %D를 사용, 기준 포인트 80,20 사용하여 더 확실한 신호를 잡는다.
130일 이동 지수평균이 상승하고 %D가 20 아래로 떨어질 때 매수하고, 130일 이동 지수평균이 하락하고 %D가 80 위로 올라갈 때 매도한다.
* 주식이 오르기 시작하는 시점을 찾아내는 것은 그리 쉬운 일이 아니다.

당일 날짜에 매수,매도 신호가 있는 종목들을 모두 검색하는 알고리즘 필요
이거 대로 주식을 매매 한다면 대체로 손해를 본다.
"""

import pandas as pd
import matplotlib.pyplot as plt, mpld3
import datetime
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from matplotlib import rc
from DB import Analyzer
from mplfinance.original_flavor import candlestick_ohlc

# DB의 모든 종목을 대입해 매수 시그널 날짜가 오늘이거나 최근인 종목 리스트를 검색해주는 기능 만들기
compName = '카카오'

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

# 한글 폰트 깨짐 방지 설정
path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우 폰트 위치
fontprop = fm.FontProperties(fname=path, size=10).get_name()
rc('font', family='nanumgothic')


plt.figure(figsize=(9, 9))
p1 = plt.subplot(3, 1, 1)
plt.title(f'Triple Screen Trading - {compName}')
plt.grid(True)

candlestick_ohlc(p1,ohlc.values, width=.6, colorup='red', colordown='blue')  # ohlc의 숫자형 일자, 시가, 고가, 저가, 종가 값을 이용해서 캔들 차트를 그린다.
p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['ema130'], color='c', label='EMA130')
for i in range(1, len(df.close)):
    if df.ema130.values[i - 1] < df.ema130.values[i] and \
            df.slow_d.values[i - 1] >= 20 > df.slow_d.values[i]: # 130일 이동 지수평균이 상승하고 %D가 20 아래로 떨어지면
        plt.plot(df.number.values[i], 0, 'r^')  # 빨간색 삼각형으로 매수 신호를 표시한다.
        print(f"(buy) date : {df.date.values[i]}, close price : {df.close.values[i]}")  # 콘솔화면에 날짜와 가격 표시
    elif df.ema130.values[i - 1] > df.ema130.values[i] and \
            df.slow_d.values[i - 1] <= 80 < df.slow_d.values[i]:  # 130일 이동 지수평균이 하락하고 %D가 80 위로 상승하면
        plt.plot(df.number.values[i], 0, 'bv')  # 파란색 감각형으로 매수 신로를 표시한다.
        print(f"(sell) date : {df.date.values[i]}, close price : {df.close.values[i]}")
plt.legend(loc='best')

p2 = plt.subplot(3, 1, 2)
plt.grid(True)
p2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.bar(df.number, df['macdhist'], color='m', label='MACD-Hist')
plt.plot(df.number, df['macd'], color='b', label='MACD')
plt.plot(df.number, df['signal'], 'g--', label='MACD-Signal')
for i in range(1, len(df.close)):
    if df.ema130.values[i - 1] < df.ema130.values[i] and \
            df.slow_d.values[i - 1] >= 20 > df.slow_d.values[i]: # 130일 이동 지수평균이 상승하고 %D가 20 아래로 떨어지면
        plt.plot(df.number.values[i], 0, 'r^')  # 빨간색 삼각형으로 매수 신호를 표시한다.
    elif df.ema130.values[i - 1] > df.ema130.values[i] and \
            df.slow_d.values[i - 1] <= 80 < df.slow_d.values[i]:  # 130일 이동 지수평균이 하락하고 %D가 80 위로 상승하면
        plt.plot(df.number.values[i], 0, 'bv')  # 파란색 감각형으로 매수 신로를 표시한다.
plt.legend(loc='best')

p3 = plt.subplot(3, 1, 3)
plt.grid(True)
p3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.plot(df.number, df['fast_k'], color='c', label='%K')
plt.plot(df.number, df['slow_d'], color='k', label='%D')
plt.yticks([0, 20, 80, 100])  # Y축 눈금을 0, 20, 80, 100으로 설정하여 스토캐스틱의 기준선을 나타낸다.
for i in range(1, len(df.close)):
    if df.ema130.values[i - 1] < df.ema130.values[i] and \
            df.slow_d.values[i - 1] >= 20 > df.slow_d.values[i]: # 130일 이동 지수평균이 상승하고 %D가 20 아래로 떨어지면
        plt.plot(df.number.values[i], 0, 'r^')  # 빨간색 삼각형으로 매수 신호를 표시한다.
    elif df.ema130.values[i - 1] > df.ema130.values[i] and \
            df.slow_d.values[i - 1] <= 80 < df.slow_d.values[i]:  # 130일 이동 지수평균이 하락하고 %D가 80 위로 상승하면
        plt.plot(df.number.values[i], 0, 'bv')  # 파란색 감각형으로 매수 신로를 표시한다.


plt.legend(loc='best')
plt.show()
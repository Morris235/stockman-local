# 단순 산점도 분석 : 선형 회귀 분석이 더 정확함
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

Stock_Index = "^DJI"

#지수 변수
Date = "2000-01-01"

yf.pdr_override()
dow = pdr.get_data_yahoo(Stock_Index, Date)


kospi = pdr.get_data_yahoo('^KS11', Date)

df = pd.DataFrame({Stock_Index: dow['Close'], 'KOSPI': kospi['Close']})

df = df.fillna(method='bfill')
df = df.fillna(method='ffill')

plt.figure(figsize=(7, 7))

plt.scatter(df[Stock_Index], df['KOSPI'], marker='.')
plt.xlabel(Stock_Index)
plt.ylabel('KOSPI')
plt.show()

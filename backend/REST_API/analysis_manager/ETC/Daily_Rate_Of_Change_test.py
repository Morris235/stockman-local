"""야후 파이낸스를 이용한(국내 주식 정보는 부정확함) 주가 일간 변동률 모듈"""
from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

yf.pdr_override()

codeX = '005930.KS'
codeY = 'MSFT'
startDate = '2020-01-04'

indicesX = pdr.get_data_yahoo(codeX,start=startDate)
indicesX_dpc = (indicesX['Close']-indicesX['Close'].shift(1)) / indicesX['Close'].shift(1) * 100
indicesX_dpc.iloc[0] = 0 #일간 변동률의 첫 번째 값인 NaN을 0으로 변경한다.
indicesX_dpc_cs = indicesX_dpc.cumsum() # 일간 변동률의 누적합을 구한다.

indicesY = pdr.get_data_yahoo(codeY,start=startDate)
indicesY_dpc = (indicesY['Close'] / indicesY['Close'].shift(1) -1) * 100
indicesY_dpc.iloc[0] = 0
indicesY_dpc_cs = indicesY_dpc.cumsum()

plt.plot(indicesX.index, indicesX_dpc_cs, 'b', label='Samsung Electronics')
plt.plot(indicesY.index, indicesY_dpc_cs, 'r--', label='Microsoft')
plt.ylabel('change %')
plt.grid(True)
plt.legend(loc='best')
plt.show()

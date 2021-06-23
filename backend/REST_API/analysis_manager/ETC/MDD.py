# 최대 손실 낙폭 (Maximum Drawdown) : 특정 기간에 발생한 최고점에서 최저점까지의 가장 큰 손실을 의미한다. *야후 파이낸스 이용
#퀀트 투자에서는 수익률을 높이는 것보다 MDD를 낮추는 것이 더 낫다고 할 만큼 중요한 지표로서, *특정 기간 동안 최대한 얼마의 손실이 날 수 있는지를 나타낸다.

#코스피의 최대 손실 낙폭
from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

yf.pdr_override()

startData = '2010-01-01'
code = '^KS11'

kospi = pdr.get_data_yahoo(code,startData)

window = 252  # 산정 기간에 해당하는 window값은 1년동안의 개장일을 252일로 어림잡아 설정했다.
peak = kospi['Adj Close'].rolling(window, min_periods=1).max()  # KOSPI 종가 칼럼에서 1년(거래일 기준) 기간 단위로 최고치 peak을 구한다.
drawdown = kospi['Adj Close']/peak - 1.0  # drawdown은 최고치(peak) 대비 현재 KOSPI 종가가 얼마나 하락했는지를 구한다.
max_dd = drawdown.rolling(window, min_periods=1).min()  # drawdown에서 1년 기간 단위로 최저치 max_dd를 구한다. 마이너스값이기 때문에 최저치가 바로 최대 손실 낙폭이 된다.

# MDD 수치
print(code, 'MDD : ', max_dd.min())
print(max_dd[max_dd==max_dd.min()])


plt.figure(figsize=(9, 7))
plt.subplot(211)  #2행 1열 중 1행에 그린다.
kospi['Close'].plot(label='{:s}'.format(code), title='{:s} MDD'.format(code), grid=True, legend=True)
plt.subplot(212) # 2행 1열중 2행에 그린다.
drawdown.plot(c='blue', label='{:s} DD'.format(code), grid=True, legend=True)
max_dd.plot(c='red', label='{:s} MDD'.format(code), grid=True, legend=True)
plt.show()
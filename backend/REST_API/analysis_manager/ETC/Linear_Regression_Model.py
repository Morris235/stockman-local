"""
사이파이 선형 회귀 분석 : 상대 지표와 얼마나 관련이 있는지 분석한다.
"""
from scipy import stats
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt

Date = "2000-01-01"

yf.pdr_override()

dow = pdr.get_data_yahoo('^DJI', Date)  #다우지수를 야후 파이낸스로부터 다운로드 한다.
kospi = pdr.get_data_yahoo('^KS11', Date)

df = pd.DataFrame({"X": dow['Close'], 'Y': kospi['Close']})  #다우존스 지수를 X칼럼으로 KOSPI 지수를 Y칼럼으로 갖는 데이터프레임을 생성한다.

df = df.fillna(method='bfill')
df = df.fillna(method='ffill')

# 결정계수가 1이면 모든 표본 관측치가 추정된 회귀선 상에만 있다는 의미. 즉, 추정된 회귀선이 변수간의 관계를 완벽히 설명한다.
#반면에 결정계수가 0이면 추정된 회귀선이 변수 사이의 관계를 전혀 설명하지 못한다는 의미다.

r_value = df['X'].corr(df['Y'])
r_squared = r_value ** 2  # #결정계수는 상관계수를 제곱해야 한다.
print('상관계수 : ', r_value)
print('그래프 신뢰도 : ', r_squared)

#상관계수 : 독립변수와 종속변수 사이의 상관관계의 정도를 나타내는 수치다. 양의 상관관계가 가장 강한 값을 1로, 음의 상관관계가 가장 강한 값을 -1로 나타내며, 상관관계가 없을 때 r은 0이다.
#A자산과 B자산의 상관관계수가 1이면, A자산 가치가 x%만큼 상승할 때 B자산 가치도 x%만큼 상승한다. A자산과 B자산의 상관관계수가 -1이면, A자산 가치가 x%만큼 상승할 때 B자산의 가치는 x%만큼 하락한다.
#A자산과 B자산의 상관관계수가 0이면 두 자산의 움직임이 서로 전혀 연관성이 없다. 즉, 상관관계수가 0에 가깝다면 분산투자를 할 때 그만큼 리스크 완화 효과를 기대할 수 있다.

regr = stats.linregress(df.X, df.Y)  #다우존스 지수X와 KOSPI지수 Y로 선형회귀 모델 객체 regr을 생성한다.  #상관계수
regr_line = f'Y = {regr.slope:.2f} * X + {regr.intercept:.2f}'  #범례에 회귀식을 표시하는 레이블 문자.

plt.figure(figsize=(7, 7))
plt.plot(df.X, df.Y, '.')  #산점도를 작은 원으로 나타낸다.
plt.plot(df.X, regr.slope * df.X + regr.intercept,'r')  #희귀선을 붉은 색으로 그린다.
plt.legend(['Indices x KOSPI', regr_line])
plt.title(f'Indices x KOSPI (R = {regr.rvalue:.2f})')
plt.xlabel('Indices')
plt.ylabel('KOSPI')
plt.show()
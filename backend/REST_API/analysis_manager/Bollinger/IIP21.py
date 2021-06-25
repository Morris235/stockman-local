"""
IIP21 : 일중강도율을 이용한 반전 매매 기법
"""
import matplotlib.pyplot as plt
from matplotlib import rc, font_manager as fm
from DB import Analyzer

# df = mkdb.get_daily_price('삼성전자', '2019-01-02')  에러 발생하는 코드 : codes를 찾을 수 없음
compName = '카카오'
mk = Analyzer.MarketDB()  #객체 생성, 변수에 저장
df = mk.get_daily_price(compName, '2021-01-01')  #df 변수에 get_daily_price() 의 DataFrame 리턴값 저장

df['MA20'] = df['close'].rolling(window=20).mean()  # 20개 종가를 이용해서 평균을 구한다.
df['stddev'] = df['close'].rolling(window=20).std()  # 20개 종가를 이용해서 표준편차를 구한 뒤 stddev 칼럼으로 df에 추가한다.
df['upper'] = df['MA20'] + (df['stddev'] * 2)  # 중간 볼린저 밴드 + (2 * 표준편차)
df['lower'] = df['MA20'] - (df['stddev'] * 2)  # 중간 볼린저 밴드 - (2 * 표준편차)
df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])  #%b = (종가 - 하단 볼린저 밴드) / (상단 볼린저 밴드 - 중간 볼린저 밴드)

df['II'] = (2 * df['close'] - df['high'] - df['low']) / (df['high'] - df['low']) * df['volume']  # 종목의 종가, 고가, 저가, 거래량을 이용해 일중 강도 II를 구한다.
df['IIP21'] = df['II'].rolling(window=21).sum() / df['volume'].rolling(window=21).sum() * 100  # 21일간의 일중 강도 II합을 21일간의 거래량 합으로 나누어 일중 강도율 II%를 구한다.
df = df.dropna()

# 한글 폰트 깨짐 방지 설정
path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우 폰트 위치
fontprop = fm.FontProperties(fname=path, size=10).get_name()
rc('font', family='NanumGothic')

plt.figure(figsize=(9, 9))
plt.subplot(3, 1, 1)  # 기존의 볼린저 밴드 차트를 3행 1열의 그리드에서 1열에 배치한다.
plt.title('Bollinger Band (20 day, 2 std) - Reversals - '+compName)
plt.plot(df.index, df['close'], 'b', label='Close')  # x 좌표는 df.index에 해당하는 종가를 y좌표로 설정해 파란색(#0000ff) 실선으로 표시한다.
plt.plot(df.index, df['upper'], 'r--', label='Upper band')  # x좌표 df.index에 해당하는 상단 볼린저 밴드값을 y 좌표로 설정해 검은 실선으로 표시한다.
plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
plt.plot(df.index, df['lower'], 'c--', label='Lower band')
plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')  # 상단 볼린저 밴드와 하단 볼린저 밴드 사이를 회색으로 칠한다.
for i in range(0, len(df.close)):
    if df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:  #
        plt.plot(df.index.values[i], df.close.values[i], 'r^')  #
    elif df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:  #
        plt.plot(df.index.values[i], df.close.values[i], 'bv')  #

plt.legend(loc='best')
plt.subplot(3, 1, 2)  # %B 차트를 3행 1열의 그리드에서 2열에 배치한다.
plt.plot(df.index, df['PB'], color='b', label=' %B')  # X좌표 df.index에 해당하는 %b 값을 y좌표로 설정해 파란(b) 실선으로 표시한다.
plt.grid(True)
plt.legend(loc='best')

"""
세 번째 차트에 표시된 일중 강도율은 기관 블록 거래자의 활동을 추적할 목적으로 만들어진 지표다. 존 볼린저는 일중 강도율을 볼린저 밴드를 확증하는 도구로 사용하는데, 
주가가 하단 볼린저 밴드에 닿을 때 일중 강도율이 +이면 매수하고, 반대로 주가가 상단 볼린저 밴드에 닿을 때 일중 강도율이 -이면 매도하라고 조언한다. 
"""
plt.subplot(3, 1, 3) # %B 차트를 3행 1열의 그리드에서 3열에 일중 강도율을 그린다.
plt.bar(df.index, df['IIP21'], color='g', label='II% 21day')  # 녹색 실선으로 21일 일중 강도율을 표시한다.
for i in range(0, len(df.close)):
    if df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0:  # %b가 0.05 보다 작고, 21일 기준 II%가 0보다 크면
        plt.plot(df.index.values[i], 0, 'r^')  # 첫 번째 그래프에 매수 시점을 나타내는 종가 위치에 빨간색 삼각형을 표시한다.
        print(f"(buy) date : {df.date.values[i]}, close price : {df.close.values[i]}")
    elif df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0:  # %b 가 0.95보다 크고, 21일 기준 II%가 0보다 작으면
        plt.plot(df.index.values[i], 0, 'bv')  # 첫 번째 그래프에 매도 시점을 나타내는 종가 위치에 파란색 삼각형을 표시한다.
        print(f"(sell) date : {df.date.values[i]}, close price : {df.close.values[i]}")
plt.grid(True)
plt.legend(loc='best')
plt.show()
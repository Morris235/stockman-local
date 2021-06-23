"""
볼린저 밴드 : 추세 추종
* 매수/매도 신호 한번만으론 상승/하락 추세가 시작됐다고 판단하기 힘들다

MFI(현금흐름지표) : 일반적으로 주가를 나타낼 때 종가를 사용하지만, 중심가격을 사용하면 트레이딩이 집중적으로 발생하는 주가 지점을 더 잘 나타낼 수 있다.
중심가격이란 일정 기간의 고가, 저가, 종가를 합한 뒤에 3으로 나눈 값이다.
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
df['TP'] = (df['high'] + df['low'] + df['close']) / 3  # 고가, 저가, 종가의 합을 3으로 나눠서 중심 가격 TP(typical price)를 구한다.
df['PMF'] = 0
df['NMF'] = 0

for i in range(len(df.close) -1):  # range 함수는 마지막 값을 포함하지 않으므로 0부터 종가 개수 -2까지 반복한다.
    if df.TP.values[i] < df.TP.values[i+1]:  # i 번쨰 중심 가격보다 i+1 번째 중심 가격이 높으면
        df.PMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]  # i+1 번째 중심 가격과 i+1번째 거래량의 곱을 i+1번째 긍정적 현금 흐름 PMF에 저장한다.
        df.NMF.values[i+1] = 0  # i+1 번째 부정적 현금 흐름 NMF 값은 0으로 저장한다.
    else:
        df.NMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
        df.PMF.values[i+1] = 0

# 10일 동안의 긍정적 현금 흐름의 합을 10일 동안의 부정적 현금 흐름의 합으로 나눈 결과를 현금 흐름 비율 MFR (money flow ratio) 칼럼에 저장한다.
df['MFR'] = (df.PMF.rolling(window=10).sum() / df.NMF.rolling(window=10).sum())
df['MFI10'] = 100 - 100 / (1 + df['MFR'])  # 10일 기준으로 현금흐름지수를 계산한 결과를 MFI10(money flow index 10) 킬람에 자징힌다.
df = df[19:]  # 19번째 행까지 NaN 이므로 값이 있는 20번쨰 행부터 사용한다.

# 한글 폰트 깨짐 방지 설정
path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우 폰트 위치
fontprop = fm.FontProperties(fname=path, size=10).get_name()
rc('font', family='nanumgothic')

plt.figure(figsize=(9, 8))
plt.subplot(2, 1, 1)  # 기존의 볼린저 밴드 차트를 2행 1열의 그리드에서 1열에 배치한다.
plt.title('Bollinger Band (20 day, 2 std) - Trend Following - '+compName)
plt.plot(df.index, df['close'], color='#0000ff', label='Close')  # x 좌표는 df.index에 해당하는 종가를 y좌표로 설정해 파란색(#0000ff) 실선으로 표시한다.
plt.plot(df.index, df['upper'], 'r--', label='Upper band')  # x좌표 df.index에 해당하는 상단 볼린저 밴드값을 y 좌표로 설정해 검은 실선으로 표시한다.
plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
plt.plot(df.index, df['lower'], 'c--', label='Lower band')
plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')  # 상단 볼린저 밴드와 하단 볼린저 밴드 사이를 회색으로 칠한다.
plt.grid(True)

for i in range(len(df.close)):
    if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:  # %b가 0.8보다 크고 10일 기준 MFI가 80 보다 크면
        plt.plot(df.index.values[i], df.close.values[i], 'r^')  # 매수시점을 나타내기 위해 첫 번째 그래프의 종가 위치에 빨간색 삼각형을 표시한다.
        print(f"(buy) date : {df.date.values[i]}, close price : {df.close.values[i]}")
    elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:  # %b 가 0.2 보다 작고 10일 기준 MFI가 20보다 작으면
        plt.plot(df.index.values[i], df.close.values[i], 'bv')  # 매도 시점을 나타내기 위해 첫 번째 그래프의 종가 위치에 파란색 삼각형을 표시한다.
        print(f"(sell) date : {df.date.values[i]}, close price : {df.close.values[i]}")
plt.legend(loc='best')

plt.subplot(2, 1, 2)  # %B 차트를 2행 1열의 그리드에서 2열에 배치한다.
# X좌표 df.index에 해당하는 %b 값을 y좌표로 설정해 파란(b) 실선으로 표시한다. +MFI 와 비교할 수 있게 %b를 그대로 표시하지 않고 100을 곱해서 푸른색 실선으로 표시한다.
plt.plot(df.index, df['PB'] * 100, 'b', label='%B x 100')
plt.plot(df.index, df['MFI10'], 'g--', label='MFI(10 day)')  # 10일 기준 MFI를 녹색 점선으로 표시한다.
plt.yticks([-20, 0, 20, 40, 60, 80, 100, 120])      # y 축 눈금을 -20 부터 120까지 20 단위로 표시한다.
for i in range(len(df.close)):
    if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:
        plt.plot(df.index.values[i], 0, 'r^')  # 0이 아닌 df.close.values[i]를 넣었을때 그래프가 그려지지 않았다 맷플롯립에 대해 숙지가 부족해서다
    elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:
        plt.plot(df.index.values[i], 0, 'bv')
plt.grid(True)
plt.legend(loc='best')
plt.show();


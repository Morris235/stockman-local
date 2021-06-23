"""
기본 볼린저 밴드
"""
import matplotlib.pyplot as plt
from DB import Analyzer

# df = mkdb.get_daily_price('삼성전자', '2019-01-02')  에러 발생하는 코드 : codes를 찾을 수 없음
compName = '카카오'
mk = Analyzer.MarketDB()  #객체 생성, 변수에 저장
df = mk.get_daily_price(compName, '2021-05-01')  #df 변수에 get_daily_price() 의 DataFrame 리턴값 저장

df['MA20'] = df['close'].rolling(window=20).mean()  # 20개 종가를 이용해서 평균을 구한다.
df['stddev'] = df['close'].rolling(window=20).std()  # 20개 종가를 이용해서 표준편차를 구한 뒤 stddev 칼럼으로 df에 추가한다.
df['upper'] = df['MA20'] + (df['stddev'] * 2)  # 중간 볼린저 밴드 + (2 * 표준편차)
df['lower'] = df['MA20'] - (df['stddev'] * 2)  # 중간 볼린저 밴드 - (2 * 표준편차)
df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])  #%b = (종가 - 하단 볼린저 밴드) / (상단 볼린저 밴드 - 중간 볼린저 밴드)
df = df[19:]  # 19번째 행까지 NaN 이므로 값이 있는 20번쨰 행부터 사용한다.

plt.figure(figsize=(9, 5))
plt.subplot(2,1,1)  # 기존의 볼린저 밴드 차트를 2행 1열의 그리드에서 1열에 배치한다.
plt.plot(df.index, df['close'], color='#0000ff', label='Close')  # x 좌표는 df.index에 해당하는 종가를 y좌표로 설정해 파란색(#0000ff) 실선으로 표시한다.
plt.plot(df.index, df['upper'], 'r--', label='Upper band')  # x좌표 df.index에 해당하는 상단 볼린저 밴드값을 y 좌표로 설정해 검은 실선으로 표시한다.
plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
plt.plot(df.index, df['lower'], 'c--', label='Lower band')
plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')  # 상단 볼린저 밴드와 하단 볼린저 밴드 사이를 회색으로 칠한다.
plt.title('Bollinger Band x Percent B(20 day, 2 std)')
plt.legend(loc='best')

plt.subplot(2,1,2)  # %B 차트를 2행 1열의 그리드에서 2열에 배치한다.
plt.plot(df.index, df['PB'], color='b', label=' %B')  # X좌표 df.index에 해당하는 %b 값을 y좌표로 설정해 파란(b) 실선으로 표시한다.

plt.grid(True)
plt.legend(loc='best')
plt.show()
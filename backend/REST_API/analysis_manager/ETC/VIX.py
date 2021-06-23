"""
VIX(Volatility Index) 공포지수란 S&P 500지수 옵션가격의향후 30일간의 기대치를 반영한 지수로 %단위로 나타낸다.
<지수가 높을수록 공포심이 높다는 의미이며 통산 20~30 정도의 범위를 평균 수준으로 보며 40~50이 바닥권이라 해석하기 때문에 반등을 기대할 수 있다.>
공포지수가 높을수록 투자자들이 투매를 하고, 주가는 기업의 가치보다 터무니없이 낮게 형성된다.
공포지수가 낮을수록 거품이 많이 형성되어 있다고 봐도 될까?
참고로 지수가 횡보할때는 큰 의미를 갖는 분석은 어렵다
"""
from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import rc, font_manager as fm
from DB.Analyzer import MarketDB as mkdb


yf.pdr_override()



startDate = '2021-05-18'
endDate = '2021-06-22'
compName = "카카오"

mk = mkdb()
compPrice = mk.get_daily_price(compName, startDate)  # DB로 부터 회사 검색

vix = pdr.get_data_yahoo('^VIX', startDate)
kospi = pdr.get_data_yahoo('^KS11', startDate)

print(vix.index)
try:
    # for idx in range(0, len(kospi.index), 1):
    #     print(f"{vix.index[idx].strftime('%Y-%m-%d')} : {vix.Close[idx]:.02f} => KOSPI CLOSE : {kospi.Close[idx]:.02f}")

    # 한글 폰트 깨짐 방지 설정
    path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우 폰트 위치
    fontprop = fm.FontProperties(fname=path, size=10).get_name()
    rc('font', family='nanumgothic')

    plt.figure(figsize=(12, 8))

    plt.subplot(311)  # 2행 1열 중 1행에 그린다.
    vix['Close'].plot(marker='o', linestyle='--', label='VIX', title='VIX 공포 지수 ', grid=True, legend=True)

    plt.subplot(312)  # 2행 1열중 2행에 그린다.
    kospi['Close'].plot(marker='o', linestyle='--', c='red', label='KOSPI', title='KOSPI 지수', grid=True, legend=True)

    plt.subplot(313)  # 2행 1열중 2행에 그린다.
    compPrice['close'].plot(marker='o', linestyle='--', c='g', label=f'{compName}', title=f'{compName} Close Price',
                            grid=True, legend=True)

    plt.tight_layout()  # 하위 플롯 간격 자동 개선
    plt.show()
except IndexError as e:
    print(e)

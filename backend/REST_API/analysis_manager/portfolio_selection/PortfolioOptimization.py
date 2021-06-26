"""
모든 연도 재무제표 연산 필요 (연도별로 12시간, 총 72시간 이상 소요 예상)
기업재무 제표를 조회(?), 조건에 따라 기업명 가져오기
조건 : 안정성, 성장성, 수익성.
판단 기준:
이슈, 화제성, 주도업종에서(업종코드 활용) 종목 가져오기
각 비율지표 시계열 분석, 연도별 시총증가율 등등. 사용자가 입력한 기준으로 쿼리(연도 지정, 각 비율 커트라인 수치). 기준을 더 세세하게 추가할 필요가 있음


가져올 기업명 개수 설정
가져온 기업명을 토대로 해당 기업들의 주가에 현대 포트폴리오 이론 적용(?)

아니면 무작위의 모든 종목을 대입해서 리스크가 적고 가장큰 이익을 내는 알고리즘은 어떨까?
포트폴리오 이론은 과거 데이터를 기반으로 계산한건데 이익을 내는데 효과가 있는지 의문 스럽지만 지금까지 계산 해본 결과 손해는 없었다. 다만 수익률은 조금 미미했다.(100만원 투자 기준)
아니면 단타 전략을 짜는게 더 낫지 않을까? 그렇다면 지금까지 얻은 데이터로 어떻게 단타 전략을 짤 수 있을까
현대 포트폴리오 이론은 수익률 보다 안정성에 더 중점을 둔 이론이다.(손실을 보지 않기 위한 종목별 비중을 달리둔 포트폴리오) 그렇기 때문에 어떤 종목이 더 오를지에 대한 분석이 아니다.

과거의 데이터로 포트폴리오를 시뮬레이션해보는 정도다. 미래가치는 알 수 없음.
"""

"""
샤프 지수 = (포트폴리오 기대 수익률 - 무위자산 수익률) / (포트폴리오 수익률의 표준편차)
*계산의 편의를 고려해 무위험률을 0으로 가정했으며, 샤프 지수는 포트폴리오의 예상 수익률을 수익률의 표준편차로 나누어서 구했다. *
예를 들어 예상 수익률이 7%이고 수익률의 표준편차가 5%인 경우, 샤프 지수는 7 / 5 = 1.4 가 된다. 샤프 지수가 높을수록 위험에 대한 보상이 더 크다.
"""
"""
효율적 투자선 이론을 개량한것으로, 위험 단위당 수익률이 가장 높은 포트폴리오는 Sharpe값이 가장 큰 행을 찾으면 되고, 
가장 안전한 포트폴리오는 Risk값이 가장 작은 행을 찾으면 된다. 
"""

# 이걸 어떻게 웹에서 사용자와 상호작용 시키지?
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from REST_API.DB.StockPriceSearcher import Market as mkdb

class PortfolioSelector:
    def __init__(self):
        self.mk = mkdb()
        self.stocks_name_list = ['카카오', 'NAVER', '셀트리온', 'LG화학']  # ex) '삼성전자', 'SK하이닉스', '현대자동차', 'NAVER'
        self.start_date = '2021-05-18'  # 당연한거지만 언제 사서 언제 파는냐에 따라 수익률이 다르다
        self.end_date = '2021-06-22'
        # 사용자가 입력해야할 예상 투자금
        self.investment = 10000000  # 투자금액이 너무 적으면 투자분산이 되지 않는다. (종목 선별 함수에 투자금액에 맞는 종목을 필터링 하는 조건을 추가시켜볼까?)
        # 랜덤하게 생성할 포트폴리오 개수
        self.portfolio_count = 30000


        # 비중 계산용
        self.df = pd.DataFrame()
        # 주가 계산용
        self.df_price = pd.DataFrame()

        # 총 예상 수익을 담을 리스트
        self.total_revenue = []
        # 총 투자금액을 담을 리스트
        self.total_investment = []

        # 실행 함수
        self.portfolio_revenue()

    # 종목 선별 함수 : 그나마 중요한건 이건데...
    def portfolio_select(self):
        try:
            #
            stocks_name_list = []
            return stocks_name_list
        except:
            return

    # 선별된 종목으로 포트폴리오 비중 계산 : 과거 데이터로 시뮬레이션 돌려보는 정도 밖에 안된다.
    def portfolio_revenue(self):
        try:
            for s in self.stocks_name_list:
                # 액면분할,유/무상 증자의 전후 주가가 뒤섞이면 수익률 계산이 어렵다. 따라서 액면분할의 영향을 피해서 검색해야한다.
                # ex) s, '2016-01-04', '2018-04-27')['close']
                self.df[s] = self.mk.get_daily_price(s, self.start_date, self.end_date)['close']

            # 종목의 수익률을 비교하려면 종가 대신 일간 변동률로 비교를 해야 하기 때문에
            # 데이터프레임에서 제공하는 pct_change() 함수를 사용해 종목들의 일간 변동률을 구한다.
            daily_ret = self.df.pct_change()  # 일간 수익률 daily_ret

            # 일간 변동률의 평균값에 252를 곱해서 연간 수익률을 구한다. 252는 미국의 1년 평균 개장일로, 우리나라 실정에 맞게 다른 숫자로 바꾸어도 무방하다.
            annual_ret = daily_ret.mean() * 248  # 연간 수익률 annual_ret (2020년 기준 248일 개장)

            # 일간 리스크는 cov() 함수를 사용해 일간 변동률의 공분산으로 구한다.
            daily_cov = daily_ret.cov()  # 일간 리스크 daily_cov

            # 연간 공분산은 일간 공분상에 252를 곱해 계산한다.
            annual_cov = daily_cov * 248  # 연간 리스크 annual_cov

            # 종목 비중을 다르게 해 포트폴리오 20,000개를 생성한다.
            # 포트폴리오 수익률, 리스크, 종목 비중을 저장할 각 리스트를 생성한다.
            port_ret = []  # 포트폴리오 수익률,
            port_risk = []  # 포트폴리오 리스크,
            port_weights = []  # 포트폴리오 목 비중
            sharpe_ratio = []  # 샤프지수 리스트

            #  매우 많은 난수를 이용해 함수의 값을 확률적으로 계산하는 것을 몬테카를로 시뮬레이션이라고 한다.
            #  다음은 몬테카를로 시뮬레이션을 이용해 포트폴리오 20,000개를 생성한 후 각각의 포트폴리오별로 수익률, 리스크, 종목 비중을 데이터프레임으로 구하는 코드다.
            for _ in range(self.portfolio_count):  # 포트폴리오 20,000개를 생성하는데 range() 함수와 for in 구문을 사용했다. for in 구문에서 반복횟수를 사용할 일이 없으면 관습적으로 _ 변수에 할당한다.
                weights = np.random.random(len(self.stocks_name_list))  # 4개의 랜덤 숫자로 구성된 배열을 생성한다.
                weights /= np.sum(weights)  # 위에서 구한 4개의 랜덤 숫자를 랜덤 숫자의 총합으로 나눠 4종목 비중의 합이 1이 되도록 조정한다.

                returns = np.dot(weights,
                                 annual_ret)  # 랜덤하게 생성한 <종목별 비중 배열>과 <종목별 연간 수익률>을 곱해 해당 포트폴리오 전체 수익률(returns)을 구한다.

                # 종목별 연간 공분산과 종목별 비중 배열을 곱한 뒤 이를 다시 종목별 비중의 전치로 곱한다.
                # 이렇게 구한 결괏값의 제곱근을 sqrt() 함수로 구하면 해당 포트폴리오 전체 리스크를 구할 수 있다. (포트폴리오 리스크 공식 참고)
                risk = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))

                # 포트폴리오 20,000개 수익률, 리스크, 종목별 비중을 각각 리스트에 추가한다.
                port_ret.append(returns)  # 수익률
                port_risk.append(risk)  # 리스크
                port_weights.append(weights)  # 종목별 비중
                sharpe_ratio.append(
                    returns / risk)  # *포트폴리오의 수익률을 리스크로 나눈 값을 샤프 지수 리스트에 추가한다.* 제대로된 계산을 하기 위해선 공부를 좀 더 해야함

            portfolio = {'Returns': port_ret, 'Risk': port_risk, 'Sharpe': sharpe_ratio}
            for i, s in enumerate(
                    self.stocks_name_list):  # i값은 0,1,2,3 순으로 변한다. 이 때 s값은 '삼성전자', 'SK하이닉스', '현대자동차', 'NAVER'순으로 변한다.
                portfolio[s] = [weights[i] for weights in
                                port_weights]  # portfolio 딕셔너리에 '삼성전자', 'SK하이닉스', '현대자동차', 'NAVER' 키 순서로 비중값을 추가한다.
            df = pd.DataFrame(portfolio)

            # 최종 생성된 df 데이터프레임을 출력하면,
            # 시총 상위 4 종목의 보유 비율에 따라 포트폴리오 20,000개가 각기 다른 리스크와 예상 수익률을 가지는 것을 확인할 수 있다.
            df = df[['Returns', 'Risk', 'Sharpe'] + [s for s in self.stocks_name_list]]  # 샤프 지수 칼럼을 데이터프레임에 추가한다.
            max_sharpe = df.loc[df['Sharpe'] == df['Sharpe'].max()]  # 샤프 지수 칼럼에서 샤프 지수값이 제일 큰 행을 max_sharpe로 정한다.
            min_risk = df.loc[df['Risk'] == df['Risk'].min()]  # 샤프 지수 칼럼에서 리스크랎이 제일 작은 행을 min_risk로 정한다.

            # max_sharpe와 min_sharpe의 포트폴리오 비중 수치표시
            # print('max_sharpe : *')
            # print(max_sharpe)
            # # print(max_sharpe['삼성전자'])
            # print('')
            #
            # print('min_sharpe : X')
            # print(min_risk)
            # print('')

            for s in self.stocks_name_list:
                # 종목별 투자금 비율계산 : min_risk(손실최소화)보다 max_sharpe(이익극대화)가 수익률과 안정성이 더 좋을수도 있다.
                stock_investment = int(self.investment * max_sharpe[s].values[0])
                # 투자금 할당률
                investment_ratio = int(round(max_sharpe[s].values[0], 2)* 100)
                self.df_price[s] = self.mk.get_daily_price(s, self.start_date, self.end_date)['close']

                # 종목별 투자금으로 매입할수 있는 종목갯수
                amount = int(stock_investment / self.df_price[s].values[0])
                # print(f"{df_price[s].name} 매입가: {df_price[s].values[0]} 할당된 투자금 : {stock_investment} 매입수: {amount}")
                buy = self.df_price[s].values[0] * amount
                sale = self.df_price[s].values[-1] * amount
                revenue = sale - buy

                print(
                    f"[{self.df_price[s].name}] 할당된 투자금: {stock_investment} ({investment_ratio}%), 매수 종가:{self.df_price[s].values[0]}, 매도 종가: {self.df_price[s].values[-1]}, 매입개수:{amount}, 매수 : {buy}, 매도 : {sale}, "
                    f"수익 : {revenue}")

                self.total_investment.append(buy)
                self.total_revenue.append(revenue)

            print('')
            print(f"투자기간 : {self.start_date} ~ {self.end_date}")
            print(f"투자 전 예치금 : {self.investment}")
            print(f"총 투자금 : {sum(self.total_investment)}")
            print(f"예상 수익금 : {sum(self.total_revenue)}")
            print(f"투자 후 예상 예치금 : {self.investment + sum(self.total_revenue)}")

            """
            df 데이터프레임을 산점도로 출력하면, 몬테카를로 시뮬레이션으로 생성한 효율적 투자선을 눈으로 확인할 수 있다. 
            scatter() 함수를 호출할 때 x축 값으로 해당 포트폴리오의 리스크, y축 값으로 예상 수익률을 넘겨주면 된다.
            """

            # # 포트폴리오의 샤프 지수에 따라 컬러맵을 'viridis' 로 표시하고 테두리는 검정(k)으로 표시한다.
            # df.plot.scatter(x='Risk', y='Returns', c='Sharpe', cmap='viridis', edgecolors='k', figsize=(11, 7),
            #                 grid=True)
            # plt.scatter(x=max_sharpe['Risk'], y=max_sharpe['Returns'], c='r', marker='*',
            #             s=300)  # 샤프 지수가 가장 큰 포트폴리오를 300 크기의 붉은 별로 표시한다.
            # plt.scatter(x=min_risk['Risk'], y=min_risk['Returns'], c='r', marker='X',
            #             s=200)  # 리스크가 제일 작은 포트폴리오를 200 크기의 붉은 엑스표로 표시한다.
            # plt.title('Portfolio Optimization')
            # plt.xlabel('Risk')
            # plt.ylabel('Expected Returns')
            # plt.show()
            return
        except:
            pass

if __name__ == '__main__':
    execution = PortfolioSelector()
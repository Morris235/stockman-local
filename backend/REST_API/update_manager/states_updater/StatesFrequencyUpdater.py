import traceback

import OpenDartReader
import FinanceDataReader as fdr  # 데이터 수집 방법 1 (크롤링) 주가, 지수등등
import pandas as pd
from bs4 import BeautifulSoup as bs
import urllib.request
import logging

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)

pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 각 연도마다 발행주식수 구하기 =>
# 주식의 총수로 확인 가능, 추가로 발행된 주식은 발행공시에서 확인가능(유, 무상 증자) 이또한 기업마다 상이하게 표시한듯함
# 다트 사업보고서-소액주주에서 보통주 총 발행주식수 확인 가능
# EPS는 보통주와 우선주의 합인 수정평균발행주식수를 이용하여 계산함. 하지만 오픈 다트에서 이 둘을 정확하게 구별 불가
# 각 연도마다 시가총액 구하기

# 시가총액, 시가, 발행주식수같은 업데이트가 비교적 자주 일어나야 하는 비율지표를 다른 지표 업데이트와 따로 내어내어 개별 업데이트 한다.
# 1. 각 비율 지표 계산에 필요한 항목들을 수집 (수집방법 찾기)
# 2. 비율 지표 계산 (연도별)
# 3. 비율 지표 업데이트
class StatesFrequencyUpdater:
    # 시가 조회 : 시장이 아직 열리지 않았다면 현재주가를 받아올수 없다
    def __init__(self):
        api_key = '1df1a3c433cb50c187e45bb35461f17a5c28f255'
        self.dart = OpenDartReader(api_key)

        self.code = '002680'
        self.year = '2015'
        self.idx = 1

        self.all_report_df = self.dart.list(self.code, start='2014-01-01', end='2021-03-31', kind='A')

        # print(self.number_of_stocks())
        print(self.stock_price())
        # <코드및 연도 순회>
        # 해당 기업 레이블에 어떻게 맞춰서 발행주식수와 계산된 비율 데이터를 넣지? 이왕 이렇게 된거 업데이트 클래스에서 한번에 처리할까?
        # 해당기업(종목코드)의 특정 기간동안의 모든 정기보고서(최종보고서)
        # start 연월일 값은 고정, end 연 값은 business_report 디렉토리의 마지막 연도명 참조, 월일은 고정 => 반복문 사용할 필요 없음

        # 코드를 순회하고 그 안에서 연도를 순회해야 하는데 코드 추출하는게 리스트 형태라는게 걸리네
        # <사업보고서 연도 순회>
        # 요청 100건당 1분 멈춰! 를 해야 한다.
        # keu word: [기재정정]사업보고서 (20nn.12), [첨부추가]사업보고서 (20nn.12), 사업보고서 (20nn.12)
        # 연도를 반복문이든 뭐든 해서 알맞게 올려야 한다.(사업보고서의 월은 12월 고정이다.)

        # ['증자', '배당', '자기주식', '최대주주', '최대주주변동', '소액주주', '임원', '직원', '임원개인보수', '임원전체보수', '개인별보수', '타법인출자']
        # div = dart.report('005930', '배당', 2020)
        #
        # print(div)

        # print(df)

        # FinanceDataReader: 해당 기업의 현재 시가만 조회하면 되기 때문에 시작일과 종료일이 같음
        # start = str(datetime(year=int(year), month=int(month), day=int(date) - 1))
        # end = start

    def stock_price(self):
        try:
            # 휴일, 공휴일을 피한 날짜 로직 필요하다
            # 각 연도마다 3월달의 휴일, 공휴일등의 날짜를 알수 있다면?
            start = self.year
            end = start

            # 재무 정산일을 기준으로 날짜를 정해야 한다. (대략 각 년도별 3월 31일) : 정확한 기준 아님
            result_df = fdr.DataReader(self.code, f'{start}-03', f'{end}-04')
            open_price = result_df['Open']  # IndexError: index 0 is out of bounds for axis 0 with size 0 발생할수 있음

            if len(open_price) > 0:
                return open_price.values[-1]
            else:
                return 0
        except:
            logging.error(traceback.format_exc())
            return 0

    def number_of_stocks(self):
        try:
            def target_rcp_no():
                try:
                    rcp_no = self.all_report_df.loc[
                        self.all_report_df['report_nm'].isin([f'사업보고서 ({self.year}.12)'])
                        | self.all_report_df['report_nm'].isin([f'사업보고서 ({self.year}.03)'])
                        | self.all_report_df['report_nm'].isin([f'사업보고서 ({self.year}.06)'])
                        | self.all_report_df['report_nm'].isin([f'사업보고서 ({self.year}.09)'])

                        | self.all_report_df['report_nm'].isin([f'[기재정정]사업보고서 ({self.year}.12)'])
                        | self.all_report_df['report_nm'].isin([f'[기재정정]사업보고서 ({self.year}.03)'])
                        | self.all_report_df['report_nm'].isin([f'[기재정정]사업보고서 ({self.year}.06)'])
                        | self.all_report_df['report_nm'].isin([f'[기재정정]사업보고서 ({self.year}.09)'])

                        | self.all_report_df['report_nm'].isin([f'[첨부정정]사업보고서 ({self.year}.12)'])
                        | self.all_report_df['report_nm'].isin([f'[첨부정정]사업보고서 ({self.year}.03)'])
                        | self.all_report_df['report_nm'].isin([f'[첨부정정]사업보고서 ({self.year}.06)'])
                        | self.all_report_df['report_nm'].isin([f'[첨부정정]사업보고서 ({self.year}.09)'])

                        | self.all_report_df['report_nm'].isin([f'[첨부추가]사업보고서 ({self.year}.12)'])
                        | self.all_report_df['report_nm'].isin([f'[첨부추가]사업보고서 ({self.year}.03)'])
                        | self.all_report_df['report_nm'].isin([f'[첨부추가]사업보고서 ({self.year}.06)'])
                        | self.all_report_df['report_nm'].isin([f'[첨부추가]사업보고서 ({self.year}.09)'])
                        ].rcept_no
                    if len(rcp_no) > 0:
                        print(rcp_no.values[0])
                        return rcp_no.values[0]
                    else:
                        return 0
                except:
                    logging.error(traceback.format_exc())
                    return 0

            if target_rcp_no() != 0:
                # 각 기업의 연도별 사업보고서의 rcp_no(접수번호) 리스트를 구한다.
                title_df = self.dart.sub_docs(target_rcp_no())[:10]
                url = title_df.loc[title_df.title.isin(['4. 주식의 총수 등'])].url

                # url 길이 체크
                if len(url) > 0:
                    url = url.values[0]
                else:
                    return 0

                print(url)
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                response = opener.open(url)

                # 테이블을 찾는 로직 추가
                soup = bs(response, 'html.parser')
                # tb_check = soup.find(border='1').find_all('th')[1].string
                tables_div = soup.find(border='1')
                table_html = str(tables_div)

                table = pd.read_html(table_html)[0]
                circulation_number_of_stocks = table.loc[9]['주식의 종류']['합계']
                print(type(circulation_number_of_stocks))

                if str(type(circulation_number_of_stocks)) == "<class 'str'>":
                    return int(circulation_number_of_stocks)
                elif str(type(circulation_number_of_stocks)) == "<class 'int'>":
                    return circulation_number_of_stocks
                elif str(type(circulation_number_of_stocks)) == "<class 'numpy.int64'>":
                    return circulation_number_of_stocks
                else:
                    return 0
            else:
                return 0
        except:
            logging.error(traceback.format_exc())
            return 0


if __name__ == '__main__':
    execution = StatesFrequencyUpdater()

# init-------------------------

# small = dart.report(krx.code.values[idx], '소액주주', year, reprt_code=REPORT_CODE)  # 총발행주식수
# 기업의 현재 시가 조회
# self.open_price = self.get_stock_price(code, start, end)


from datetime import datetime
import traceback
import OpenDartReader
import FinanceDataReader as fdr
import pandas as pd
import logging
import csv

# 콘솔에 판다스 결과값 최대 표시 설정
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)


# 시가조회를 위해 하루에 한번씩 업데이트가 필요?
# 이제 전체 정제된(refined_state_files) 재무제표에 접근할수 있게됐다.
# 자동으로 읽어드리는 코드 만들기 (dir 손보기)
# 4년간의 재무제표 데이터로 지표 계산하기
# 칼럼 수정하기
# 계산된 지표 업데이트 하기
class StatesUpdater:
    def __init__(self):
        # 테이블 create query 작성

        # 현재 날짜 객체
        year = format(datetime.today().year)
        month = format(datetime.today().month)
        date = format(datetime.today().day)

        api_key = '1df1a3c433cb50c187e45bb35461f17a5c28f255'
        dart = OpenDartReader(api_key)

        # state_year dir : 연간 디렉토리명 넣기기        self.state_dir = 'refined_state_files/state_year/statements_success.txt'
        self.income_dir = 'refined_state_files/state_year/income_success.txt'
        self.state_code_dir = 'refined_state_files/state_year/state_code_list.txt'

        # 보고서 타입
        # FIRST_QUARTER = 11013
        # HALF_QUARTER = 110123
        # THIRD_QUARTER = 11014
        REPORT_CODE = 11011  # 연간 보고서

        # 데이터프레임 가공용 기업 코드리스트, read_csv로 읽으면 기업코드중 앞부분인 0이 생략됨. 왜그런지 이유를 모그렜음 -> 0000은 뭔가 헥사같은 예약어
        with open(self.state_code_dir, encoding='euc-kr', mode='r') as code_file:
            code_lines = code_file.readlines()
            state_code_list = list(map(lambda s: s.strip(), code_lines))

        # 재무상태 기업코드 리스트를 칼럼으로 가공
        self.state_code_columns = []
        with open(self.state_dir, mode='r', encoding='euc-kr') as state_f:
            state_rdr = csv.reader(state_f)
            for state_line in state_rdr:
                self.state_code_columns.append(state_line[1])

        # 손익 계산서 기업코드 리스트를 칼럼으로 가공
        self.income_code_columns = []
        with open(self.income_dir, mode='r', encoding='euc-kr') as income_f:
            income_rdr = csv.reader(income_f)
            for income_line in income_rdr:
                self.income_code_columns.append(income_line[1])

        # krx 전체 공시 기업코드 조회용
        krx = self.read_krx_code()
        krx_count = len(state_code_list)

        # 해당 기업의 현재 시가만 조회하면 되기 때문에 시작일과 종료일이 같음
        start = str(datetime(year=int(year), month=int(month), day=int(date) - 1))
        end = start

        # 기업코드 순회 & csv 읽기
        for idx in range(krx_count):
            code = state_code_list[idx]
            # 기업의 현재 시가 조회
            self.open_price = self.get_stock_price(code, start, end)
            # 총발행주식 조회
            self.small = dart.report(krx.code.values[idx], '소액주주', year, reprt_code=REPORT_CODE)
            self.read_state_csv(code)

    # 시장이 아직 열리지 않았다면 현재주가를 받아올수 없다
    @staticmethod
    def get_stock_price(code: str, start_year: str, end_year: str):
        df = fdr.DataReader(code, start_year, end_year)
        open_price = df['Open'].values[0]
        return open_price

    # small 변수 콜백함수 처리 필요 : 콜백처리 안하면 5번 반복할 때마다 에러
    def get_stock_count(self):
        try:
            stock_total_number = self.small['stock_tot_co'].str.replace(',', '')
            stock_total_number = int(stock_total_number)
            return stock_total_number
        except:
            return 0

    @staticmethod
    def read_krx_code():
        """KRX로부터 상장법인목록 파일을 읽어와서 데이터프레임으로 반환"""
        url = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
        krx = pd.read_html(url, header=0)[0]  # [0]을 붙임으로써 결괏값을 데이터프레임으로 받는다.
        krx = krx[['종목코드', '회사명']]  # 종목코드 칼럼과 회사명만 남긴다. 데이터프레임에 [[]]을 사용하면 특정 칼럼만 뽑아서 원하는 순서대로 재구성할 수 있다.
        krx = krx.rename(columns={'종목코드': 'code', '회사명': 'company'})  # 한글 칼럼명을 영문 칼럼명으로 변경
        krx.code = krx['code'].map(
            '{:06d}'.format)  # krx_list[0].종목코드 = krx_list[0].종목코드.map('{:06d}'.format) # 종목코드의 앞자리 0 보정 : {:06f}는 여석 자리 숫자 형식으로 표현하되 빈 앞 자리를 0으로 채우라는 뜻
        krx = krx.sort_values(by='code')  # 종목코드 칼럼의 값으로 정렬, 기본은 오름차순 정렬이며, ascending=False를 인수로 추가하면 내림차순으로 정렬된다.
        return krx

    # 이걸 어떻게 읽어서 기업별로 지표를 구하지? + 시가,발행주식수도 반복문으로 받아서 함께 계산해줘야 한다.
    # 데이터프레임으로 만들어서 기업코드를 인덱스로 사용하고, 반복문으로 순회, 해당 값들을 딕셔너리로 만들어서 필요한 지표 계산
    # 반복문이기 때문에 기업별 트리를 만들던지 바로 계산해서 db에 올리던지 해야함. 어떤 형태여야 하지?
    def read_state_csv(self, code):
        # 분기마다 비율 지표를 표시 해야한다 ex) 2018 2019 2020 -> 결국 curr, last, before 전부를 구해서 계산해야함 -> before의 지표값을 구할려면 2017년 값들도 가져와야함
        try:
            # 재무상태 보고서
            state_csv = pd.read_csv(self.state_dir, engine='python', header=None,
                                    names=['comp_nm', 'code', 'type', 'acc_nm', 'target_nm',
                                           'set_base_date', 'sec_code', 'sec_nm', 'mk',
                                           'curr_year', 'last_year', 'year_before'],
                                    sep=',',
                                    encoding='euc-kr')
            state_csv.drop(columns=['acc_nm'], inplace=True)
            state_csv['code'] = self.state_code_columns

            # 손익 계산서
            income_csv = pd.read_csv(self.income_dir, engine='python', header=None,
                                     names=['comp_nm', 'code', 'type', 'acc_nm', 'target_nm',
                                            'set_base_date', 'sec_code', 'sec_nm', 'mk',
                                            'curr_year', 'last_year', 'year_before'],
                                     sep=',',
                                     encoding='euc-kr')
            income_csv.drop(columns=['acc_nm'], inplace=True)
            income_csv['code'] = self.income_code_columns

            # <공통>
            # 기업명
            comp_nm = \
                state_csv.loc[state_csv['code'].isin([code]), 'comp_nm'].values[0]
            # 기업코드
            comp_code = code
            # 보고서 타입
            rp_type = state_csv.loc[state_csv['code'].isin([code]), 'type'].values[0]
            # 보고서 기준 일자
            set_base_date = state_csv.loc[state_csv['code'].isin([code]), 'set_base_date'].values[0]
            # 업종코드
            sec_code = state_csv.loc[state_csv['code'].isin([code]), 'sec_code'].values[0]
            # 업종명
            sec_nm = state_csv.loc[state_csv['code'].isin([code]), 'sec_nm'].values[0]
            # 시장구분
            mk = state_csv.loc[state_csv['code'].isin([code]), 'mk'].values[0]

            # <재무상태 보고서>
            # 금년도 자산총계
            assets = \
                state_csv.loc[
                    state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['자산총계']), 'curr_year'].values[0]
            # 전년도 자산총계
            last_assets = \
                state_csv.loc[
                    state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['자산총계']), 'last_year'].values[0]
            # 자본총계
            equity = \
                state_csv.loc[
                    state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['자본총계']), 'curr_year'].values[0]
            # 부채총계
            liabilities = \
                state_csv.loc[
                    state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['부채총계']), 'curr_year'].values[0]
            # 유동부채
            current_liabilities = \
                state_csv.loc[
                    state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['유동부채']), 'curr_year'].values[0]
            # 유동자산
            current_assets = \
                state_csv.loc[
                    state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['유동자산']), 'curr_year'].values[0]

            # <손익 계산서>
            # 매출액
            revenue = state_csv.loc[state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['매출액']), 'curr_year'].values[0]
            # 전년도 매출액
            last_revenue = state_csv.loc[state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['매출액']), 'last_year'].values[0]
            # 당기순이익
            net_income = state_csv.loc[state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['당기순이익']), 'curr_year'].values[0]
            # 전년도 당기순이익
            last_net_income = state_csv.loc[state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['당기순이익']), 'last_year'].values[0]
            # 주당손익
            eps = state_csv.loc[state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['주당손익']), 'curr_year'].values[0]
            # 금융수익
            fin_income = state_csv.loc[state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['금융수익']), 'curr_year'].values[0]
            # 금융비용
            fin_cost = state_csv.loc[state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['금융비용']), 'curr_year'].values[0]

            print(comp_nm, comp_code, rp_type, set_base_date, sec_code, sec_nm, mk,
                  assets, last_assets, equity, liabilities, current_liabilities, current_assets)
        # 비율지표 계산
        # 한 기업씩 기업의 지표를 DB에 업데이트

        except:
            logging.error(traceback.format_exc())

    def cal_ratio(self):
        return


if __name__ == '__main__':
    execution = StatesUpdater()

    # execution.read_state_csv('000020')
    # execution.read_income_csv()

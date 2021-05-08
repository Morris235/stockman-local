import time
from datetime import datetime
import os
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

        # 디렉토리/파일 이름 리스트 : 연도별 보고서 순환용
        self.year_list = self.read_refined_year_file()

        # self.fin_txt_list = txt_dic.get('refined_fin_list')
        # self.income_txt_list = txt_dic.get('refined_income_list')

        # state_year dir : 연간 디렉토리명 넣기기 -> 보고서 연도별 순회, 보고서 안에 curr_year, last_year, before_year 값들로 비율 계산하기

        # 보고서 타입
        # FIRST_QUARTER = 11013
        # HALF_QUARTER = 110123
        # THIRD_QUARTER = 11014
        REPORT_CODE = 11011  # 연간 보고서

        # krx 전체 공시 기업코드 조회용


        # FinanceDataReader: 해당 기업의 현재 시가만 조회하면 되기 때문에 시작일과 종료일이 같음
        start = str(datetime(year=int(year), month=int(month), day=int(date) - 1))
        end = start

        krx = self.read_krx_code()

        # refined 보고서 순회
        for position in range(len(self.year_list)):
            year = self.year_list[position]
            # fin_txt_name = self.fin_txt_list[position]
            # income_txt_name = self.income_txt_list[position]

            # refined 보고서에서 추출한 기업코드 리스트
            state_code_list = self.get_state_code_list(year)
            krx_count = len(state_code_list)

            # 기업코드 순회 & csv 읽기
            for idx in range(krx_count):
                if (idx + 1) % 100 != 0:
                    code = state_code_list[idx]
                    # 기업의 현재 시가 조회
                    self.open_price = self.get_stock_price(code, start, end)
                    # 총발행주식 조회 : 연도별 조회 필요 year은 보고서의 연도다. 보고서내의 curr, last, before 연도가 필요함
                    small = dart.report(krx.code.values[idx], '소액주주', year, reprt_code=REPORT_CODE)
                    self.read_state_csv(code, year, small)
                else:
                    time.sleep(60)


    # 시장이 아직 열리지 않았다면 현재주가를 받아올수 없다
    @staticmethod
    def get_stock_price(code: str, start_year: str, end_year: str):
        df = fdr.DataReader(code, start_year, end_year)
        open_price = df['Open'].values[0]
        return open_price

    def get_state_code_list(self, year):
        # 연도별 기업 코드 리스트 순회
        # 만약 기업코드가 state엔 없는데 income에는 있다면? : 재점검 필요
        state_code_dir = f'refined_state_files/state_year/{year}/{year}_05_state_code_list.txt'
        with open(state_code_dir, encoding='euc-kr', mode='r') as code_file:
            code_lines = code_file.readlines()
            state_code_list = list(map(lambda s: s.strip(), code_lines))
            return state_code_list

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

    @staticmethod
    def read_refined_year_file():
        # 순서
        # 01_state_succ, 02_income_succ, 03_cash_succ, 04_flu_succ,
        # 05_{state,income,cash,flu}_code_list, 06_{state,income,cash,flu}_filed, 07_{state,income,cash,flu}_no_code

        # refined_fin_list = []
        # refined_income_list = []
        # refined_cash_list = []
        # refined_flu_list = []

        # 디렉토리명에서 연도 얻기
        state_year_dir = 'refined_state_files/state_year'
        year_list = os.listdir(state_year_dir)

        # for year in year_list:
        #     path_dir = f'refined_state_files/state_year/{year}'
        #     file_list = os.listdir(path_dir)

            # refined_fin_list.append(file_list[0])
            # refined_income_list.append(file_list[1])

        # # txt_list 크기 = n년치 보고서 -> n개
        # # 접근 = [0]=>보고서 종류 (0~n), [0][n]=>연도별 보고서
        # year_report_name_txt_dict = {'refined_fin_list': refined_fin_list,
        #                              'refined_income_list': refined_income_list,
        #                              'year_list': year_list}

        return year_list

    # 이걸 어떻게 읽어서 기업별로 지표를 구하지? + 시가,발행주식수도 반복문으로 받아서 함께 계산해줘야 한다.
    # 데이터프레임으로 만들어서 기업코드를 인덱스로 사용하고, 반복문으로 순회, 해당 값들을 딕셔너리로 만들어서 필요한 지표 계산
    # 반복문이기 때문에 기업별 트리를 만들던지 바로 계산해서 db에 올리던지 해야함. 어떤 형태여야 하지?
    def read_state_csv(self, code, year, small):
        # 분기마다 비율 지표를 표시 해야한다 ex) 2018 2019 2020 -> 결국 curr, last, before 전부를 구해서 계산해야함 -> before의 지표값을 구할려면 2017년 값들도 가져와야함
        try:
            # refined 보고서 연도별 path
            state_dir = f'refined_state_files/state_year/{year}/{year}_01_statements_success.txt'
            income_dir = f'refined_state_files/state_year/{year}/{year}_02_income_success.txt'
            
            # 재무상태 기업코드 리스트를 칼럼으로 가공
            state_code_columns = []
            with open(state_dir, mode='r', encoding='euc-kr') as state_f:
                state_rdr = csv.reader(state_f)
                for state_line in state_rdr:
                    state_code_columns.append(state_line[1])

            # 손익 계산서 기업코드 리스트를 칼럼으로 가공
            income_code_columns = []
            with open(income_dir, mode='r', encoding='euc-kr') as income_f:
                income_rdr = csv.reader(income_f)
                for income_line in income_rdr:
                    income_code_columns.append(income_line[1])




            # 재무상태 보고서 가공
            state_csv = pd.read_csv(state_dir, engine='python', header=None,
                                    names=['comp_nm', 'code', 'type', 'acc_nm', 'target_nm',
                                           'set_base_date', 'sec_code', 'sec_nm', 'mk',
                                           'curr_year', 'last_year', 'year_before'],
                                    sep=',',
                                    encoding='euc-kr')
            state_csv.drop(columns=['acc_nm'], inplace=True)
            state_csv['code'] = state_code_columns

            # 손익 계산서 가공
            income_csv = pd.read_csv(income_dir, engine='python', header=None,
                                     names=['comp_nm', 'code', 'type', 'acc_nm', 'target_nm',
                                            'set_base_date', 'sec_code', 'sec_nm', 'mk',
                                            'curr_year', 'last_year', 'year_before'],
                                     sep=',',
                                     encoding='euc-kr')
            income_csv.drop(columns=['acc_nm'], inplace=True)
            income_csv['code'] = income_code_columns

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

            # 해당기업 전체 발행주식수
            # small 변수 콜백함수 처리 필요 : 콜백처리 안하면 5번 반복할 때마다 에러
            # 개인 : 일 10,000건 (서비스별 한도가 아닌 오픈 API 23종 전체 서비스 기준)
            # 일일한도를 준수하더라도 서비스의 안정적인 운영을 위하여 과도한 네트워크 접속(분당 100회 이상)은 서비스 이용이 제한
            def stock_count():
                try:
                    stock_total_number = small['stock_tot_co'].str.replace(',', '')
                    stock_total_number = int(stock_total_number)
                    return stock_total_number
                except:
                    return 0

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
            revenue = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['매출액']), 'curr_year'].values[0]
            # 전년도 매출액
            last_revenue = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['매출액']), 'last_year'].values[0]
            # 당기순이익
            net_income = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['당기순이익']), 'curr_year'].values[0]
            # 전년도 당기순이익
            last_net_income = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['당기순이익']), 'last_year'].values[0]
            # 주당손익
            eps = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['주당손익']), 'curr_year'].values[0]
            # 금융수익
            fin_income = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['금융수익']), 'curr_year'].values[0]
            # 금융비용
            fin_cost = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['금융비용']), 'curr_year'].values[0]
            # 영업비용
            cost_of_sales = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업비용']), 'curr_year'].values[0]
            # 영업외손익
            non_oper_income = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업외손익']), 'curr_year'].values[0]
            # 영업외비용
            non_oper_expenses = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업외비용']), 'curr_year'].values[0]
            # 법인세비용
            corporate_tax = income_csv.loc[income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['법인세비용']), 'curr_year'].values[0]

            print(f'{year} 기업명 : {comp_nm}, 코드 : {comp_code}, 보고서 타입 : {rp_type}, 결산기준일 : {set_base_date}, 업종코드 : {sec_code}, 업종명 : {sec_nm}, 시장 :{mk},'
                  f'자산 : {assets}, 전년도 자산 : {last_assets}, 자본 : {equity}, 부채 : {liabilities}, 유동부채 : {current_liabilities}, 유동자산 : {current_assets}, 발행주식수 : {stock_count()},')
            print('')
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

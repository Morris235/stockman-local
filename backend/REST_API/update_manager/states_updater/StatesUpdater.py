import csv
import logging
import os
import time
import traceback
import urllib.request
import FinanceDataReader as fdr
import OpenDartReader
import pandas as pd

from bs4 import BeautifulSoup as bs
from REST_API.DB.Connector import connector
from datetime import datetime

# 콘솔에 판다스 결과값 최대 표시 설정
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)


# 시가조회를 위해 하루에 한번씩 전체 데이터 업데이트가 필요함 -> 따로 클래스로 만들어서 시가 데이터만 업데이트 하면 된다.
# 칼럼 수정하기
# 계산된 지표 업데이트 하기
class StatesUpdater:

    def __init__(self):
        print('Company State Updating')

        # 다트 조회용 키
        api_key = '1df1a3c433cb50c187e45bb35461f17a5c28f255'
        self.dart = OpenDartReader(api_key)

        # 디렉토리/파일 이름 리스트 : 연도별 보고서 순환용
        state_year_dir = 'refined_state_files/year'
        self.year_list = os.listdir(state_year_dir)


        # 이전 업데이트 연도부터 진행을 위한 로직(개발중)
        # 2015~2020
        del self.year_list[:5]

        # 1분당 유통주식수 크롤링 제한 횟수, 다트 api 호출 카운트 변수 선언
        scraping_limit, self.dart_call_count = 10, 0

        # refined 디렉토리 전체 보고서 순회 -> 이 구조는 느린 처리속도를 가진다 (3중 반복문 : 전체 dir, 기업코드, 비율계산)
        # 각 연도 디렉토리마다 state code 를 순회해야 하기 때문에 지금으로썬 이 반복문이 쓰이는건 어쩔수 없음 => 진짜?
        for position in range(len(self.year_list)):  # 연도 순회
            year = self.year_list[position]
            # check_dir = self.check_dir_name(self.year_list[position])
            progress_count = 0

            # refined 보고서에서 추출한 기업코드 리스트
            state_code_list = self.read_state_code_list(year)
            krx_count = len(state_code_list)

            # 기업코드 순회 & csv 읽기
            # last update [2021-06-11 16:55:12] 0320 / 2165 008830 (2020 REPLACE UPDATE)
            for code in state_code_list:  # 코드 순회
                progress_count += 1
                start_time = time.time()

                # 한번 종목을 순회할 때마다 7.5번의 스크랩핑과 다트 api 호출을 보낸다.
                if progress_count % scraping_limit != 0:
                    self.update_ratio(code, year)
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{tmnow}] {progress_count :04d} / {krx_count} ({round((progress_count/krx_count) * 100, 2)}%) {code} ({year} REPLACE UPDATE) 소요시간: {round(time.time() - start_time, 2)} 초")
                else:
                    # else 문에서도 update_ratio 함수를 호출하지 않으면 멈출때마다 해당 종목은 업데이트 되지 않는다.
                    self.update_ratio(code, year)
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{tmnow}] {progress_count :04d} / {krx_count} ({round((progress_count/krx_count) * 100, 2)}%) {code} ({year} REPLACE UPDATE) 소요시간: {round(time.time() - start_time, 2)} 초, 1분 스크랩핑 대기")
                    time.sleep(61)

            print('')

    # 취득에 성공한 기업코드 리스트 리턴
    @staticmethod
    def read_state_code_list(year):
        # 연도별 기업 코드 리스트 순회
        # 만약 기업코드가 state 엔 없는데 income 에는 있다면? : 재점검 필요
        state_code_dir = f'refined_state_files/year/{year}/{year}_05_state_code_list.txt'
        with open(state_code_dir, encoding='euc-kr', mode='r') as code_file:
            code_lines = code_file.readlines()
            state_code_list = list(map(lambda s: s.strip(), code_lines))
            return state_code_list

    # 필터링되어 저장한 재무항목 csv 파일을 데이터프레임으로 리턴
    @staticmethod
    def convert_to_dataframe(year):
        try:
            # init 의 refined 보고서 순회의 큰 흐름
            # refined 보고서 연도별 path
            state_dir = f'refined_state_files/year/{year}/{year}_01_statements_success.txt'
            income_dir = f'refined_state_files/year/{year}/{year}_02_income_success.txt'

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
                                           'sec_code', 'sec_nm', 'mk',
                                           'curr_year', 'last_year', 'year_before'],
                                    sep=',',
                                    encoding='euc-kr')
            state_csv.drop(columns=['acc_nm'], inplace=True)
            state_csv['code'] = state_code_columns

            # 손익 계산서 가공
            income_csv = pd.read_csv(income_dir, engine='python', header=None,
                                     names=['comp_nm', 'code', 'type', 'acc_nm', 'target_nm',
                                            'sec_code', 'sec_nm', 'mk',
                                            'curr_year', 'last_year', 'year_before'],
                                     sep=',',
                                     encoding='euc-kr')
            income_csv.drop(columns=['acc_nm'], inplace=True)
            income_csv['code'] = income_code_columns

            refined_report = {'state_csv': state_csv, 'income_csv': income_csv}
            return refined_report
        except:
            pass
            # logging.error(traceback.format_exc())



    # 증가율 계산 함수
    @staticmethod
    def cal_increase_rate(x, y):
        # 금년도가 전년도 보다 못 벌었는데 수식에 의해서 부호가 +가 되거나, 금년도가 전년도보다 잘 벌었는데도 -가 될수 있음. 이를 보정해줘야 한다.
        # ex) 당기: -300만, 전기: -100만,  (-)300+(-)100 / -100 * 100 = -20%, 실제론 30% 증가했지만 표기상으로 -30%가 될수도 있다.
        try:
            if y != 0:
                result = (x - y) / y * 100
                if x > y and 0 > result:
                    result = -result
                    return result
                elif x > y and 0 < result:
                    return result
                elif x < y and 0 < result:
                    result = -result
                    return result
                elif x < y and 0 > result:
                    return result
                else:
                    return result
            else:
                return 0.0

        except:
            logging.error(traceback.format_exc())
            return 0.0

    # 비율 계산 함수
    @staticmethod
    def cal_rate(x, y):
        try:
            # 양쪽 수가 모두 0이 아닐때 계산식 성립 'str'클래스는 '__and__'를 정의하지 않으므로 '&'연산자는 인스턴스에서 사용할 수 없습니다.
            # 이게 효율성이 있나? 관리는 편할지 몰라도 말이야. NoneType 체크해야지~ 값이 0인지 체크해야지~시발거
            # 하지만 cal_ratios 에서 에러가 나는거 보다 낫지 않나?
            if x != 0:
                if y != 0:
                    rate = (x / y) * 100
                    return round(rate, 2)
                else:
                    return 0.0
            else:
                return 0.0

        except:
            logging.error(traceback.format_exc())
            return 0.0



    # 디렉토리 유무 체크
    @staticmethod
    def check_dir_name(year_dir_name):
        root_dir = 'refined_state_files/year'
        root_file_list = os.listdir(root_dir)

        # file_list 가 비어 있다면 True
        if len(root_file_list) <= 0:
            return True
        # 루트 디렉토리에 해당 파일이 있다면 False
        elif year_dir_name in root_file_list:
            return False
        # 없다면 True
        else:
            return True

    # 지배기업지분이 있을경우 지배기업지분 리턴, 별도는 일반 당기순이익 리턴
    def select_net_profit(self, code, year):
        try:
            year_before_last = year - 1
            curr_owners_profit_test = self.read_refined_income(code=code, year=year,
                                                          quarter='curr_year').get(
                'ifrs_owners_of_parent')

            # 지배기업지분을 표시한 경우 지배기업지분 항목 리턴
            if curr_owners_profit_test != 0:
                curr_owners_profit_test = self.read_refined_income(code=code, year=year,
                                                                   quarter='curr_year').get(
                    'ifrs_owners_of_parent')
                last_owners_profit = self.read_refined_income(code=code, year=year,
                                                              quarter='last_year').get(
                    'ifrs_owners_of_parent')
                before_owners_profit = self.read_refined_income(code=code, year=year,
                                                                quarter='year_before').get(
                    'ifrs_owners_of_parent')

                if year_before_last > 2014:
                    before_owners_last_profit = self.read_refined_income(code=code, year=year_before_last,
                                                                         quarter='year_before').get(
                        'ifrs_owners_of_parent')
                else:
                    before_owners_last_profit = 0

                profit_dict = {
                    'curr_year': curr_owners_profit_test,
                    'last_year': last_owners_profit,
                    'year_before': before_owners_profit,
                    'before_last': before_owners_last_profit
                }

                return profit_dict

            # 지배기업지분을 기록하지 않은 경우 일반 당기순이익 항목 리턴
            else:
                curr_net_profit = self.read_refined_income(code=code, year=year,
                                                           quarter='curr_year').get(
                    'net_profit')
                last_net_profit = self.read_refined_income(code=code, year=year,
                                                           quarter='last_year').get(
                    'net_profit')
                before_net_profit = self.read_refined_income(code=code, year=year,
                                                             quarter='year_before').get('net_profit')
                if year_before_last > 2014:
                    before_last_profit = self.read_refined_income(code=code, year=year_before_last,
                                                                  quarter='year_before').get(
                        'net_profit')
                else:
                    before_last_profit = 0

                profit_dict = {
                    'curr_year': curr_net_profit,
                    'last_year': last_net_profit,
                    'year_before': before_net_profit,
                    'before_last': before_last_profit
                }
                return profit_dict

        # 데이터가 없는 경우
        except:
            # logging.error(traceback.format_exc())
            profit_dict = {
                'curr_year': 0.0,
                'last_year': 0.0,
                'year_before': 0.0,
                'before_last': 0.0
            }
            return profit_dict

    # 공통 항목 조회및 dict 형태로 리턴 함수
    def read_refined_common(self, code, year):
        try:
            refined_df = self.convert_to_dataframe(year)
            state_csv = refined_df.get('state_csv')
            income_csv = refined_df.get('income_csv')

            # <공통>
            # 기업명
            comp_nm = \
                state_csv.loc[state_csv['code'].isin([code]), 'comp_nm'].values[0]
            # 보고서 타입
            state_rp_type = state_csv.loc[state_csv['code'].isin([code]), 'type'].values[0]
            income_rp_type = income_csv.loc[income_csv['code'].isin([code]), 'type'].values[0]

            # 보고서 기준 일자
            # set_base_date = state_csv.loc[state_csv['code'].isin([code]), 'set_base_date'].values[0]
            # 업종코드
            sec_code = state_csv.loc[state_csv['code'].isin([code]), 'sec_code'].values[0]
            # 업종명
            sec_nm = state_csv.loc[state_csv['code'].isin([code]), 'sec_nm'].values[0]
            # 시장구분
            mk = state_csv.loc[state_csv['code'].isin([code]), 'mk'].values[0]

            common_item = {'comp_nm': comp_nm,
                           'state_rp_type': state_rp_type,
                           'income_rp_type': income_rp_type,
                           'sec_code': sec_code,
                           'sec_nm': sec_nm,
                           'mk': mk}

            return common_item
        except:
            # logging.error(traceback.format_exc())
            return

    # 필터링된 재무상태 항목 조회및 dict 리턴
    def read_refined_state(self, code, year, quarter):
        try:
            refined_df = self.convert_to_dataframe(year)
            # 해당 기업의 해당 연도의 모든 분기, 사업보고서 요청
            state_csv = refined_df.get('state_csv')

            # <재무상태 보고서 항목>
            # 자산총계
            def assets():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['자산총계']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 자본총계
            def equity():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['자본총계']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 부채총계
            def liabilities():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['부채총계']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 유동부채
            def current_liabilities():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['유동부채']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 유동자산
            def current_assets():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['유동자산']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 재고자산
            def inventories():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['재고자산']), quarter].values[
                        0]
                    return item
                except:
                    # logging.error(traceback.format_exc())
                    return 0

            state_item = {'assets': assets(),
                          'equity': equity(),
                          'liabilities': liabilities(),
                          'current_liabilities': current_liabilities(),
                          'current_assets': current_assets(),
                          'inventories': inventories()
                          }

            return state_item
        except:
            logging.error(traceback.format_exc())
            state_item = {'assets': 0,
                          'equity': 0,
                          'liabilities': 0,
                          'current_liabilities': 0,
                          'current_assets': 0,
                          'inventories': 0
                          }
            return state_item

    # 필터링된 손익 항목 조회및 dict 리턴
    def read_refined_income(self, code, year, quarter):
        try:
            refined_df = self.convert_to_dataframe(year)
            income_csv = refined_df.get('income_csv')

            # <손익 계산서 항목>
            # 매출액
            def revenue():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['매출액']), quarter].values[0]
                    return item
                except:
                    return 0

            # 당기순이익
            def net_profit():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['당기순이익']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 주당손익 (별도 계산이 필요없기 때문에 값이 없을경우 0을 리턴)
            def eps():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['주당손익']), quarter].values[0]
                    return item
                except:
                    return 0

            # 금융수익
            def fin_income():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['금융수익']), quarter].values[0]
                    return item
                except:
                    return 0

            # 금융비용
            def fin_cost():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['금융비용']), quarter].values[0]
                    return item
                except:
                    return 0

            # 영업이익
            def operating_profit():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업이익']), quarter].values[0]
                    return item
                except:
                    return 0

            # 영업비용
            def cost_of_sales():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업비용']), quarter].values[0]
                    return item
                except:
                    return 0

            # 영업외손익
            def non_oper_income():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업외손익']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 영업외비용
            def non_oper_expenses():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업외비용']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 법인세비용
            def corporate_tax():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['법인세비용']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 지배기업지분 -> 값이없는 경우 일반 당기순이익으로 계산
            def ifrs_owners_of_parent():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['지배기업지분']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 비지배기업지분 -> 어디에 써야하더라?
            def ifrs_non_controlling_interests():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['비지배기업지분']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            # 매출총이익
            def gross_profit():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['매출총이익']), quarter].values[
                        0]
                    return item
                except:
                    return 0

            income_item = {'revenue': revenue(),
                           'net_profit': net_profit(),
                           'eps': eps(),
                           # 'fin_income': fin_income(),
                           # 'fin_cost': fin_cost(),
                           'cost_of_sales': cost_of_sales(),
                           # 'non_oper_income': non_oper_income(),
                           # 'non_oper_expenses': non_oper_expenses(),
                           # 'corporate_tax': corporate_tax(),
                           'ifrs_owners_of_parent': ifrs_owners_of_parent(),
                           # 'ifrs_non_controlling_interests': ifrs_non_controlling_interests(),
                           'gross_profit': gross_profit(),
                           'operating_profit': operating_profit()}
            return income_item
        except:
            logging.error(traceback.format_exc())
            income_item = {'revenue': 0,
                           'net_profit': 0,
                           'eps': 0,
                           'fin_income': 0,
                           'fin_cost': 0,
                           'cost_of_sales': 0,
                           'non_oper_income': 0,
                           'non_oper_expenses': 0,
                           'corporate_tax': 0,
                           'ifrs_owners_of_parent': 0,
                           'ifrs_non_controlling_interests': 0,
                           'gross_profit': 0,
                           'operating_profit': 0}
            return income_item

    #  계산된 비율 dict 리턴
    def cal_ratios(self, code, year, quarter_year, quarter_str_list):
        try:
            # <계산에 필요한 항목>
            net_profit = self.select_net_profit(code, year).get(quarter_str_list)  # 당기순이익 (연결, 별도 구분)
            read_refined_income = self.read_refined_income(code, year, quarter_str_list)
            read_refined_state = self.read_refined_state(code, year, quarter_str_list)
            # div = self.dart.report(code, '배당', quarter_year)  # 다트 : 배당에 관한 사항 조회

            # 손익 항목
            revenue = read_refined_income.get('revenue')  # 매출액(영업수익)
            operating_profit = read_refined_income.get('operating_profit')  # 영업이익
            gross_profit = read_refined_income.get(
                'gross_profit')  # 매출총이익
            # cost_of_sales = read_refined_income.get(
            #     'cost_of_sales')  # 영업비용
            eps = read_refined_income.get('eps')  # 주당손익

            # 재무상태 항목
            equity = read_refined_state.get('equity')  # 자본총계
            assets = read_refined_state.get('assets')  # 자산총계
            current_assets = read_refined_state.get(
                'current_assets')  # 유동자산
            inventories = read_refined_state.get('inventories')  # 재고자산
            liabilities = read_refined_state.get('liabilities')  # 부채총계
            current_liabilities = read_refined_state.get(
                'current_liabilities')  # 유동부채

            # <항목 계산>
            # 당좌자산
            def current_asset_cal():
                # 유동자산 - 재고자산
                try:
                    if current_assets != 0:
                        if inventories != 0:
                            return current_assets - inventories
                        else:
                            return 0
                    else:
                        return 0
                except:
                    # logging.error(traceback.format_exc())
                    return 0

            #  평균 자기자본
            def average_equity():
                try:
                    if equity != 0:
                        curr_equity = equity
                        last_equity = self.read_refined_state(code, year, 'last_year').get('equity')

                        result = (curr_equity + last_equity) / 2
                        return round(result, 2)
                    else:
                        return 0.0
                except:
                    return 0.0

            # <안정성 지표>
            # 유동비율
            def current_ratio():
                # 유동자산 / 유동부채 * 100
                try:
                    return self.cal_rate(current_assets, current_liabilities)
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 부채비율 -확인
            def debt_ratio():
                # 부채총계 / 자본총계 * 100
                try:
                    return self.cal_rate(liabilities, equity)
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 당좌비율 -확인
            def quick_ratio():
                # (당좌자산{유동자산 - 재고자산} / 유동부채) * 100
                try:
                    return self.cal_rate(current_asset_cal(), current_liabilities)
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 자기자본비율 -확인
            def bis():
                # 자본총계 / 자산총계 * 100
                try:
                    return self.cal_rate(equity, assets)
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # <성장성 지표>
            # 매출증가율 -확인
            def sales_growth_rate():
                # (금년도 영업수익(매출) - 전년도 영업수익(매출)) / 전년도 영업수익 * 100
                try:
                    year_before_last = year - 1
                    curr_revenue = self.read_refined_income(code, year, 'curr_year').get('revenue')
                    last_revenue = self.read_refined_income(code, year, 'last_year').get('revenue')
                    before_revenue = self.read_refined_income(code, year, 'year_before').get('revenue')

                    curr = self.cal_increase_rate(curr_revenue, last_revenue)
                    last = self.cal_increase_rate(last_revenue, before_revenue)

                    # 2015년 보고서 디렉토리부터 계산
                    if year_before_last > 2014:
                        before_last_revenue = self.read_refined_income(code=code, year=year_before_last,
                                                                       quarter='curr_year').get('revenue')

                        before = self.cal_increase_rate(before_revenue, before_last_revenue)

                        revenue_dict = {year: round(curr, 2),
                                        year - 1: round(last, 2),
                                        year - 2: round(before, 2)}

                        return revenue_dict
                    # 2014년 보고서 디렉토리가 없으므로 2015년도 보고서의 year_before 칼럼에 속하는 2013년도의 비율은 계산할수 없다.
                    else:
                        revenue_dict = {year: round(curr, 2),
                                        year - 1: round(last, 2),
                                        year - 2: 0.0}
                        return revenue_dict
                except:
                    logging.error(traceback.format_exc())
                    assets_dict = {year: 0.0,
                                   year - 1: 0.0,
                                   year - 2: 0.0
                                   }
                    return assets_dict

            # 총자산증가율 -확인
            def asset_growth_rate():
                # (금년도 자산총계 - 전년도 자산총계) / 전년도 자산총계 * 100
                try:
                    # 모든 파라미터를 전달하지 않으면 에러 발생
                    year_before_last = year - 1
                    curr_assets = self.read_refined_state(code, year, 'curr_year').get('assets')
                    last_assets = self.read_refined_state(code, year, 'last_year').get('assets')
                    before_assets = self.read_refined_state(code, year, 'year_before').get('assets')

                    curr = self.cal_increase_rate(curr_assets, last_assets)
                    last = self.cal_increase_rate(last_assets, before_assets)

                    # 2015년 보고서 디렉토리부터 계산
                    if year_before_last > 2014:
                        before_last_assets = self.read_refined_state(code=code, year=year_before_last,
                                                                     quarter='curr_year').get('assets')
                        before = self.cal_increase_rate(before_assets, before_last_assets)

                        assets_dict = {year: round(curr, 2),
                                       year - 1: round(last, 2),
                                       year - 2: round(before, 2)}

                        return assets_dict
                    # 2014년 보고서 디렉토리가 없으므로 2015년도 보고서의 year_before 칼럼에 속하는 2013년도의 비율은 계산할수 없다.
                    else:
                        assets_dict = {year: round(curr, 2),
                                       year - 1: round(last, 2),
                                       year - 2: 0.0
                                       }
                        return assets_dict
                except:
                    logging.error(traceback.format_exc())
                    assets_dict = {year: 0.0,
                                   year - 1: 0.0,
                                   year - 2: 0.0
                                   }
                    return assets_dict

            # 순이익 증가율(지배기업지분이 있을경우 지배기업지분으로 계산) -확인
            def net_profit_growth_rate():
                # (금년도 당기순이익 - 전년도 당기순이익) / 전년도 당기순이익 * 100
                # 전녀도 지배기업지분 항목을 구하지 못해서 일반 당기순이익을 구했다면 계산이 안맞지 않나?
                try:
                    profit = self.select_net_profit(code, year)  # 당기순이익 셀렉터 함수 호출

                    curr_year = profit.get('curr_year')
                    last_year = profit.get('last_year')
                    year_before = profit.get('year_before')
                    before_last = profit.get('before_last')

                    curr = self.cal_increase_rate(curr_year, last_year)
                    last = self.cal_increase_rate(last_year, year_before)
                    before = self.cal_increase_rate(year_before, before_last)

                    owner_net_profit_dict = {
                        year: round(curr, 2),
                        year - 1: round(last, 2),
                        year - 2: round(before, 2)}
                    return owner_net_profit_dict

                # 데이터가 없는 경우
                except:
                    logging.error(traceback.format_exc())
                    assets_dict = {year: 0.0,
                                   year - 1: 0.0,
                                   year - 2: 0.0
                                   }
                    return assets_dict

            # <수익성 지표>
            # 총자산이익률 -확인
            def roa():
                # (당기?)순이익 / 자산총계 * 100
                try:
                    # select_net_profit 을 이 함수내에서 항상 재선언해서 사용할것
                    profit = self.select_net_profit(code, year)  # 당기순이익 셀렉터 함수 호출
                    profit = profit.get(quarter_str_list)  # 당기순이익

                    return self.cal_rate(profit, assets)
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 매출액총이익률 -확인
            def gross_margin():
                # 매출액총이익 / 영업수익(매출액) * 100
                # 이익 : 얼마를 벌어서 얼마를 쓰고 남은 돈이 얼마인가?
                # 수익 : 얼마나 벌어들였냐
                # 매출총이익과 영업이익은 기업 가치 측면에서 중요함
                try:
                    return self.cal_rate(gross_profit, revenue)
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # <기업가치 관련 지수>
            # 자기자본이익률 -확인
            def roe():
                # 당기순이익 / 자기자본 * 100
                # 당기순이익 / 평균자기자본 * 100 (평균자기자본 = (전기 자기자본 + 당기자기자본) / 2)
                # 당기순이익 = 일정기간 동안에 기업이 창출한 순이익
                try:
                    # select_net_profit 을 이 함수내에서 항상 재선언해서 사용할것
                    profit = self.select_net_profit(code, year)  # 당기순이익 셀렉터 함수 호출
                    profit = profit.get(quarter_str_list)  # 당기순이익

                    if average_equity() != 0.0:
                        if profit != 0:
                            return self.cal_rate(profit, average_equity())
                        else:
                            return 0.0
                    else:
                        return 0.0
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 총자산회전율 -확인
            def asset_turnover():
                # 영업수익(매출) / 자산총계 * 100
                try:
                    return self.cal_rate(revenue, assets)
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 유통주식수 합계 : dart_api 사용 (다트 호출건수 체크및 시스템 멈춤 기능 포함)
            def number_of_stocks():
                try:
                    # 다트 호출 횟수 카운트 : 다트 객체와 같은 스코프에 있어야 카운트 가능함 : 이걸 함수화 할까?
                    self.dart_call_count += 1

                    # 다트 api 호출건수 1만건이 되면 자정까지 시스템 멈춰!
                    if (self.dart_call_count-1) >= 10000:
                        sec_hour = (time.localtime().tm_hour * 3600)
                        sec_minn = (time.localtime().tm_min * 60)
                        sec = time.localtime().tm_sec
                        now_sec = sec_hour + sec_minn + sec
                        sleep_sec = 86400 - now_sec
                        sleep_time = round(sleep_sec / 3600, 2)

                        print(f"다트 API 호출이 {self.dart_call_count-1} 건을 초과했으므로 현 시점부터 {sleep_time} 시간 동안 대기 합니다.")
                        time.sleep(sleep_sec)
                        self.dart_call_count = 0  # 초기화

                    end_year = format(datetime.today().year)

                    # 원인 모를 IndexError 발생, 하지만 rcp_no는 제대로 가져오므로 예외처리를 통해 리턴 : 원인 규명 필요
                    def target_url():
                        try:
                            rp_year = str(quarter_year)

                            # 해당 기업의 해당 연도의 모든 분기, 사업보고서 요청
                            request_report_df = self.dart.list(code, start='2014-01-01', end=f'{end_year}-03-31',
                                                               kind='A')  # end 값은 당년도

                            # 해당 연도 사업보고서의 rcept_no 추출 => IndexError: index 0 is out of bounds for axis 0 with size 0
                            rcp_no = request_report_df.loc[
                                request_report_df['report_nm'].isin([f'사업보고서 ({rp_year}.12)'])
                                | request_report_df['report_nm'].isin([f'사업보고서 ({rp_year}.03)'])
                                | request_report_df['report_nm'].isin([f'사업보고서 ({rp_year}.06)'])
                                | request_report_df['report_nm'].isin([f'사업보고서 ({rp_year}.09)'])

                                | request_report_df['report_nm'].isin([f'[기재정정]사업보고서 ({rp_year}.12)'])
                                | request_report_df['report_nm'].isin([f'[기재정정]사업보고서 ({rp_year}.03)'])
                                | request_report_df['report_nm'].isin([f'[기재정정]사업보고서 ({rp_year}.06)'])
                                | request_report_df['report_nm'].isin([f'[기재정정]사업보고서 ({rp_year}.09)'])

                                | request_report_df['report_nm'].isin([f'[첨부추가]사업보고서 ({rp_year}.12)'])
                                | request_report_df['report_nm'].isin([f'[첨부추가]사업보고서 ({rp_year}.03)'])
                                | request_report_df['report_nm'].isin([f'[첨부추가]사업보고서 ({rp_year}.06)'])
                                | request_report_df['report_nm'].isin([f'[첨부추가]사업보고서 ({rp_year}.09)'])

                                | request_report_df['report_nm'].isin([f'[첨부정정]사업보고서 ({rp_year}.12)'])
                                | request_report_df['report_nm'].isin([f'[첨부정정]사업보고서 ({rp_year}.03)'])
                                | request_report_df['report_nm'].isin([f'[첨부정정]사업보고서 ({rp_year}.06)'])
                                | request_report_df['report_nm'].isin([f'[첨부정정]사업보고서 ({rp_year}.09)'])
                                ].rcept_no

                            if len(rcp_no) > 0:
                                # 각 기업의 연도별 사업보고서의 rcp_no(접수번호) 리스트를 구한다.
                                title_df = self.dart.sub_docs(rcp_no.values[0])[
                                           :10]  # AttributeError: 'int' object has no attribute 'isdecimal' 발생
                                rcp_url = title_df.loc[title_df.title.isin(['4. 주식의 총수 등'])].url

                                return rcp_url.values[0]
                            else:
                                return 0

                        except:
                            logging.error(traceback.format_exc())
                            return 0

                    # rcp_no 를 취득하지 못한 경우 0을 리턴


                        # url 길이 체크
                        # if len(url) > 0:
                        #     url = url.values[0]
                        # else:
                        #     return 0
                    # 웹페이지에 테이블 태그가 없을 경우 혹은 브라우저가 아닐경우 응답을 하지 않아서 ValueError: No tables found 발생.
                    # 테이블이 정말 없는 경우를 제외하고 Request를 통해 브라우저인것 처럼 요청을 보내야한다.
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-Agent',
                                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')]
                    response = opener.open(target_url())

                    # 테이블을 찾는 로직 추가
                    soup = bs(response, 'html.parser')
                    tables_div = soup.find(border='1')  # border=1 이 아닐수도 있음. 찾는 조건을 변경해야 할수 있음. 테이블이 두개 있는 경우는?
                    table_html = str(tables_div)

                    # 테이블 html 정보를 문자열로 변경
                    table = pd.read_html(table_html)[0]
                    circulation_number_of_stocks = table.loc[9]['주식의 종류']['합계']

                    return int(circulation_number_of_stocks)

                    # circulation_number_of_stocks 의 타입 체크후 정수형으로 리턴
                    # if str(type(circulation_number_of_stocks)) == "<class 'str'>":
                    #     return int(circulation_number_of_stocks)
                    # elif str(type(circulation_number_of_stocks)) == "<class 'int'>":
                    #     return circulation_number_of_stocks
                    # elif str(type(circulation_number_of_stocks)) == "<class 'numpy.int64'>":
                    #     return circulation_number_of_stocks
                    # else:
                    #     return 0

                except:
                    # ValueError: No tables found 발생할 경우 해당 페이지를 분석하여 그에 맞춰서 유통주식수를 가져와야 하나?
                    # print(f"code: {code}, url: {target_url()}")
                    logging.error(traceback.format_exc())
                    return 0

            # 주당순자산 -확인
            def bps():
                # 순자산(자본총계) / 발행주식수
                try:
                    if equity != 0:
                        if number_of_stocks() != 0:
                            result = equity / number_of_stocks()
                            return round(result, 2)
                        else:
                            return 0.0
                    else:
                        return 0.0
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 주가순자산 비율
            def pbr():
                try:
                    # 주가 / bps
                    if bps() != 0:
                        if stock_price() != 0:
                            result = stock_price() / bps()
                            return round(result, 2)
                        else:
                            return 0.0
                    else:
                        return 0.0
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 시가 조회 : 시장이 아직 열리지 않았다면 현재주가를 받아올수 없다
            def stock_price():
                try:
                    # 휴일, 공휴일을 피한 날짜 로직 필요하다
                    start = f"{quarter_year}-03"
                    end = f"{quarter_year}-04"

                    # 재무 정산일을 기준으로 날짜를 정해야 한다. (대략 각 년도별 3월 31일) : 정확한 기준 아님
                    result_df = fdr.DataReader(code, start, end)
                    open_price = result_df['Open']  # index -1 is out of bounds for axis 0 with size 0 발생

                    return open_price.values[-1]

                except:
                    return 0

            # 배당- 테스트중

            # # 보통주 주당 현금배당금 (우선주는 기업마다 다르지만 대략 보통주의 1~2% 가량 더 줄수 있음)
            # def common_dps():
            #     try:
            #         result = div.loc[
            #             div['se'].isin(['주당 현금배당금(원)'])  # str.contains 방식으로 바꿔야할 수도 있음
            #             & div['stock_knd'].isin(['보통주'])
            #         ].thstrm.values[0]
            #
            #         return int(result)
            #     except:
            #         return 0
            #
            # # 보통주 현금 배당수익률
            # def common_yield():
            #     try:
            #         result = div.loc[
            #             div['se'].isin(['현금배당수익률(%)'])  # str.contains 방식으로 바꿔야할 수도 있음
            #             & div['stock_knd'].isin(['보통주'])
            #             ].thstrm.values[0]
            #
            #         return float(result)
            #     except:
            #         return 0.0
            #
            # # 현금배당성향 (연결 우선)
            # def div_payout_ratio():
            #     try:
            #         result = div.loc[
            #             div['se'].isin(['(연결)현금배당성향(%)'])  # str.contains 방식으로 바꿔야할 수도 있음
            #             | div['se'].isin(['(별도)현금배당성향(%)'])
            #             ].thstrm.values[0]
            #         return float(result)
            #     except:
            #         return 0.0

            # eps 항목이 손익계산서에 없을경우 계산 함수 결과값 적용

            # 주당순이익 (보고서에서 바로 구할수 있으나, 없을경우 계산하기) -좀더 확인 필요

            # 예상 순이익을 알면 예상 EPS를 계산할수 있다. -> 회사 회계팀에 찾아가서 물어보지 않고는 알기 힘들다. 딥러닝으로 계산 못하나?

            # 주당수익
            def eps_cal():
                # 당기 순이익 / 발행주식수
                try:
                    profit = self.select_net_profit(code, year)  # 당기순이익 셀렉터 함수 호출
                    profit = profit.get(quarter_str_list)  # 당기순이익

                    if eps == 0:
                        if profit != 0:
                            if number_of_stocks() != 0:
                                return round(profit / number_of_stocks(), 2)
                            else:
                                return 0
                        else:
                            return 0
                    else:
                        return eps
                except:
                    logging.error(traceback.format_exc())
                    return 0

            # 주당 수익비율 -확인
            def per():
                # 별도는 연결과 달리 지배주주와 비지배주주 구분이 없다.
                # 따라서 당기 순이익을 찾아 PER을 구하면 된다.
                # 하지만 연결의 경우 지배와 비지배 당기순이익을 구분지어서 계산을 해야 한다.
                # 주가 / 주당 순이익(eps)
                try:
                    if stock_price() != 0:
                        if eps_cal() != 0:
                            result = stock_price() / eps_cal()
                            return round(result, 2)
                        else:
                            return 0.0
                    else:
                        return 0.0
                except:
                    logging.error(traceback.format_exc())
                    return 0.0

            # 시가총액
            def mk_cap():
                try:
                    if number_of_stocks() != 0:
                        if stock_price() != 0:
                            result = stock_price() * number_of_stocks()
                            return result
                        else:
                            return 0
                    else:
                        return 0
                except:
                    logging.error(traceback.format_exc())
                    return 0

            result_dict = {
                'current_asset': current_asset_cal(),
                'gross_profit': gross_profit,
                'net_profit': net_profit,
                'operating_profit': operating_profit,
                'current_ratio': current_ratio(),
                'debt_ratio': debt_ratio(),
                'quick_ratio': quick_ratio(),
                'bis': bis(),
                'sales_growth_rate': sales_growth_rate().get(quarter_year),
                'asset_growth_rate': asset_growth_rate().get(quarter_year),
                'net_profit_growth_rate': net_profit_growth_rate().get(quarter_year),
                'per': per(),
                'roa': roa(),
                'roe': roe(),
                'eps': eps_cal(),
                'bps': bps(),
                'pbr': pbr(),
                'mk_cap': mk_cap(),
                'gross_margin': gross_margin(),
                'asset_turnover': asset_turnover(),
                'liabilities': liabilities,
                'number_of_stocks': number_of_stocks()
            }
            return result_dict
        except:
            logging.error(traceback.format_exc())
            pass

    # 재무비율 업데이트 : 메인
    def update_ratio(self, code, year):
        try:
            # 각 기업마다 2013~20nn 년까지 1년씩의 비율 계산값을 리턴
            quarter_str_list = ['curr_year', 'last_year', 'year_before']  # 각 분기별 값 추출하기 위한 변수
            quarter_diff_dict = {'curr_year': 0, 'last_year': 1, 'year_before': 2}  # 분기별 연도 계산하기 위한 변수
            quarter_count = len(quarter_str_list)
            tmnow = datetime.now().strftime('%Y-%m-%d')
            year = int(year)  # 전달받은 year 인자를 int 형으로 변환


            # <공통: 현재 순회중인 기업정보>
            common = self.read_refined_common(code, year)

            comp_nm = common.get('comp_nm')
            state_rp_type = common.get('state_rp_type')  # 연결, 별도로 보여질수 있도록 해야한다.
            sec_code = common.get('sec_code')
            sec_nm = common.get('sec_nm')
            mk = common.get('mk')

            # 2014년 사업보고서는 없기 때문에 2015년 보고서는 2013~2015년도의 비율지표 값을 업데이트하고,
            # 이후 부터는(2016~20nn) 당혜 년도 비율지표 계산값만 업데이트 한다.
            # 2013~20nn 년도까지 기업별로 순서대로 업데이트 된다.
            # 이걸 2015 디렉토리부터 적용하면 어떻게 되지? 14 13 년도 데이터는 날라간다. 계산처리도 하지 않는다.
            if year >= 2015:  # 2016년도 디렉토리 라면
                quarter_count = 1
                quarter_str_list = ['curr_year']

            # 분기 년도 순회
            # init(): 연도순회 <- update_ratio(): 코드순회 <- cal_ratio() <- read_refined_income(), read_refined_state()
            # 처음 시퀸스는 종목코드가 전달되고 그 종목코드에 대한 3년치 (13,14,15) 재무값을 추출, 두번째 부터는 15년 이후 연도의 재무값을 순서대로 추출
            for position in range(quarter_count):
                diff = quarter_diff_dict.get(quarter_str_list[position])
                quarter_year = year - diff  # 분기 년도 계산
                # 네트워크 체크 로직을 여기에 두면 전체 반복이 멈춘다.

                # code: 종목코드, year: 각 분기, 값추출용,
                # quarter_year: year과 비슷함. 분기 숫자 연도,
                # quarter_str_list: curr, last, before_last 분기문자 재무값 추출용
                cal_ratios = self.cal_ratios(code, year, quarter_year, quarter_str_list[position])

                current_asset = cal_ratios.get('current_asset')  # 당좌자산
                net_profit = cal_ratios.get('net_profit')  # 당기순이익
                gross_profit = cal_ratios.get('gross_profit')  # 매출총이익
                operating_profit = cal_ratios.get('operating_profit')  # 영업이익
                liabilities = cal_ratios.get('liabilities')  # 부채총액
                current_ratio = cal_ratios.get('current_ratio')  # 당좌비율
                debt_ratio = cal_ratios.get('debt_ratio')  # 부채비율
                quick_ratio = cal_ratios.get('quick_ratio')  # 당좌비율
                bis = cal_ratios.get('bis')  # 자기자본비율
                sales_growth_rate = cal_ratios.get('sales_growth_rate')  # 매출증가율
                asset_growth_rate = cal_ratios.get('asset_growth_rate')  # 총자산증가율
                net_profit_growth_rate = cal_ratios.get('net_profit_growth_rate')  # 순이익증가율
                eps = cal_ratios.get('eps')  # 주당손익
                bps = cal_ratios.get('bps')  # 주당순자산
                roa = cal_ratios.get('roa')  # 총자산이익률
                gross_margin = cal_ratios.get('gross_margin')  # 매출액총이익률
                roe = cal_ratios.get('roe')  # 자기자본 이익률
                asset_turnover = cal_ratios.get('asset_turnover')  # 자산회전률
                number_of_stocks = cal_ratios.get('number_of_stocks')  # 유통주식 개수
                pbr = cal_ratios.get('pbr')  # 주가총자산비율
                per = cal_ratios.get('per')  # 주가수익비율
                mk_cap = cal_ratios.get('mk_cap')  # 시가총액

                with connector.cursor() as curs:
                    # update 는 업데이트 날짜에 맞쳐서 자동생성
                    sql = f"REPLACE INTO company_state (code, year, sec, sec_nm, company_nm, rp_type, mk, last_update, " \
                          f"current_asset, gross_profit, net_profit, operating_profit, liabilities, mk_cap, number_of_stocks, " \
                          f"current_ratio, debt_ratio, quick_ratio, bis, " \
                          f"sales_growth_rate, asset_growth_rate, net_profit_growth_rate, " \
                          f"eps, roa, gross_margin, pbr, per, " \
                          f"roe, bps, asset_turnover) " \
                          f"VALUES ('{code}', '{quarter_year}', '{sec_code}', '{sec_nm}', '{comp_nm}', '{state_rp_type}', '{mk}', '{tmnow}', " \
                          f"'{current_asset}', '{gross_profit}', '{net_profit}', '{operating_profit}', '{liabilities}', '{mk_cap}', '{number_of_stocks}', " \
                          f"'{current_ratio}', '{debt_ratio}', '{quick_ratio}', '{bis}', " \
                          f"'{sales_growth_rate}', '{asset_growth_rate}', '{net_profit_growth_rate}', " \
                          f"'{eps}', '{roa}', '{gross_margin}', '{pbr}', '{per}', " \
                          f"'{roe}', '{bps}', '{asset_turnover}')"
                    curs.execute(sql)
                    connector.commit()
            return
        except:
            logging.error(traceback.format_exc())
            return


if __name__ == '__main__':
    execution = StatesUpdater()

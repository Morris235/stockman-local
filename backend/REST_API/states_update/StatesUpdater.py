from datetime import datetime
import pymysql
import os
import traceback
import pandas as pd
import logging
import csv

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
        print('Company State Update Start')
        self.conn = pymysql.connect(host='localhost', port=3306, db='STOCKS', user='root', passwd='Lsm11875**',
                                    charset='utf8', autocommit=True)

        # 디렉토리/파일 이름 리스트 : 연도별 보고서 순환용
        state_year_dir = 'refined_state_files/state_year'
        self.year_list = os.listdir(state_year_dir)

        # 상장된 전체 기업코드
        krx = self.read_krx_code()

        # refined 전체 보고서 순회 -> 이 구조는 느린 처리속도를 가진다 (3중 반복문 : 전체 dir, 기업코드, 비율계산)
        for position in range(len(self.year_list)):
            year = self.year_list[position]
            check_dir = self.check_dir_name(self.year_list[position])

            # refined 보고서에서 추출한 기업코드 리스트
            state_code_list = self.read_state_code_list(year)
            krx_count = len(state_code_list)

            # 기업코드 순회 & csv 읽기
            for idx in range(krx_count):
                code = state_code_list[idx]
                self.update_ratio(code, year)

                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{tmnow}] {idx + 1 :04d} / {krx_count} code: {code} ({year} REPLACE UPDATE)")
            print('')

    # 취득에 성공한 기업코드 리스트 리턴
    @staticmethod
    def read_state_code_list(year):
        # 연도별 기업 코드 리스트 순회
        # 만약 기업코드가 state 엔 없는데 income 에는 있다면? : 재점검 필요
        state_code_dir = f'refined_state_files/state_year/{year}/{year}_05_state_code_list.txt'
        with open(state_code_dir, encoding='euc-kr', mode='r') as code_file:
            code_lines = code_file.readlines()
            state_code_list = list(map(lambda s: s.strip(), code_lines))
            return state_code_list

    # 현재 상장된 모든 krx 기업 코드 리턴
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

    # 필터링되어 저장한 재무항목 csv 파일을 데이터프레임으로 리턴
    @staticmethod
    def convert_to_dataframe(year):
        try:
            # init 의 refined 보고서 순회의 큰 흐름
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

    # 증가율 수식 보정
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
            return 0.0

    # 디렉토리 유무 체크
    @staticmethod
    def check_dir_name(year_dir_name):
        root_dir = 'refined_state_files/state_year'
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
            owner_is_none = str(type(self.read_refined_income(code=code, year=year,
                                                              quarter='curr_year').get(
                'ifrs_owners_of_parent')))

            # 지배기업지분을 표시한 경우 지배기업지분 항목 리턴
            if owner_is_none != "<class 'NoneType'>":
                curr_owners_profit = self.read_refined_income(code=code, year=year,
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
                    'curr_year': curr_owners_profit,
                    'last_year': last_owners_profit,
                    'year_before': before_owners_profit,
                    'before_last': before_owners_last_profit
                }

                return profit_dict

            # 지배기업지분을 기록하지 않은 경우 일반 당기순이익 항목 리턴
            else:
                curr_net_profit = self.read_refined_income(code=code, year=year,
                                                           quarter='curr_year').get(
                    'net_income')
                last_net_profit = self.read_refined_income(code=code, year=year,
                                                           quarter='last_year').get(
                    'net_income')
                before_net_profit = self.read_refined_income(code=code, year=year,
                                                             quarter='year_before').get('net_income')
                if year_before_last > 2014:
                    before_last_profit = self.read_refined_income(code=code, year=year_before_last,
                                                                  quarter='year_before').get(
                        'net_income')
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
                    pass

            # 자본총계
            def equity():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['자본총계']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 부채총계
            def liabilities():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['부채총계']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 유동부채
            def current_liabilities():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['유동부채']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 유동자산
            def current_assets():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['유동자산']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 재고자산
            def inventories():
                try:
                    item = state_csv.loc[
                        state_csv['code'].isin([code]) & state_csv['target_nm'].isin(['재고자산']), quarter].values[
                        0]
                    return item
                except:
                    # logging.error(traceback.format_exc())
                    pass

            state_item = {'assets': assets(),
                          'equity': equity(),
                          'liabilities': liabilities(),
                          'current_liabilities': current_liabilities(),
                          'current_assets': current_assets(),
                          'inventories': inventories()}

            return state_item
        except:
            pass

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
                    pass

            # 당기순이익
            def net_income():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['당기순이익']), quarter].values[
                        0]
                    return item
                except:
                    pass

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
                    pass

            # 금융비용
            def fin_cost():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['금융비용']), quarter].values[0]
                    return item
                except:
                    pass

            # 영업이익
            def operating_profit():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업이익']), quarter].values[0]
                    return item
                except:
                    pass

            # 영업비용
            def cost_of_sales():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업비용']), quarter].values[0]
                    return item
                except:
                    pass

            # 영업외손익
            def non_oper_income():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업외손익']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 영업외비용
            def non_oper_expenses():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['영업외비용']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 법인세비용
            def corporate_tax():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['법인세비용']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 지배기업지분 -> 값이없는 경우 일반 당기순이익으로 계산
            def ifrs_owners_of_parent():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['지배기업지분']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 비지배기업지분 -> 어디에 써야하더라?
            def ifrs_non_controlling_interests():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['비지배기업지분']), quarter].values[
                        0]
                    return item
                except:
                    pass

            # 매출총이익
            def gross_profit():
                try:
                    item = income_csv.loc[
                        income_csv['code'].isin([code]) & income_csv['target_nm'].isin(['매출총이익']), quarter].values[
                        0]
                    return item
                except:
                    pass

            income_item = {'revenue': revenue(),
                           'net_income': net_income(),
                           'eps': eps(),
                           'fin_income': fin_income(),
                           'fin_cost': fin_cost(),
                           'cost_of_sales': cost_of_sales(),
                           'non_oper_income': non_oper_income(),
                           'non_oper_expenses': non_oper_expenses(),
                           'corporate_tax': corporate_tax(),
                           'ifrs_owners_of_parent': ifrs_owners_of_parent(),
                           'ifrs_non_controlling_interests': ifrs_non_controlling_interests(),
                           'gross_profit': gross_profit(),
                           'operating_profit': operating_profit()}
            return income_item
        except:
            return

    # 비율 계산된 dict 리턴
    def cal_ratio(self, code, year, quarter_year, quarter_str_list):
        global result_dict
        try:
            # <계산에 필요한 항목>
            revenue = self.read_refined_income(code, year, quarter_str_list).get('revenue')  # 매출액(영업수익)
            profit = self.select_net_profit(code, year).get(quarter_str_list)  # 당기순이익 (연결, 별도 구분)
            operating_profit = self.read_refined_income(code, year, quarter_str_list).get('operating_profit')  # 영업이익
            equity = self.read_refined_state(code, year, quarter_str_list).get('equity')  # 자본총계
            assets = self.read_refined_state(code, year, quarter_str_list).get('assets')  # 자산총계
            gross_profit = self.read_refined_income(code, year, quarter_str_list).get(
                'gross_profit')  # 매출액총이익
            cost_of_sales = self.read_refined_income(code, year, quarter_str_list).get(
                'cost_of_sales')  # 영업비용
            current_assets = self.read_refined_state(code, year, quarter_str_list).get(
                'current_assets')  # 유동자산
            inventories = self.read_refined_state(code, year, quarter_str_list).get('inventories')  # 재고자산
            liabilities = self.read_refined_state(code, year, quarter_str_list).get('liabilities')  # 부채총계
            current_liabilities = self.read_refined_state(code, year, quarter_str_list).get(
                'current_liabilities')  # 유동부채
            eps = self.read_refined_income(code, year, quarter_str_list).get('eps')  # 주당손익

            # <항목 계산>
            # 당좌자산 -확인
            def current_asset_cal():
                # 유동자산 - 재고자산
                try:
                    return current_assets - inventories
                except:
                    # logging.error(traceback.format_exc())
                    return 0

            # 매출총액, 매출총이익 -확인
            def total_sales_cal():
                # 영업수익 - 영업비용
                try:
                    return revenue - cost_of_sales
                except:
                    return 0



            # <안정성 지표>
            # 유동비율 -확인
            def current_ratio():
                # 유동자산 / 유동부채 * 100
                try:
                    result = current_assets / current_liabilities * 100
                    return round(result, 3)
                except:
                    return 0.0

            # 부채비율 -확인
            def debt_ratio():
                # 부채총계 / 자본총계 * 100
                try:
                    result = liabilities / equity * 100
                    return round(result, 3)
                except:
                    return 0.0

            # 당좌비율 -확인
            def quick_ratio():
                # (당좌자산{유동자산 - 재고자산} / 유동부채) * 100
                try:
                    result = current_asset_cal() / current_liabilities * 100
                    return round(result, 3)
                except:
                    return 0.0

            # 자기자본비율 -확인
            def bis():
                # 자본총계 / 자산총계 * 100
                try:
                    result = equity / assets * 100
                    return round(result, 3)
                except:
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

                        revenue_dict = {year: round(curr, 3),
                                        year - 1: round(last, 3),
                                        year - 2: round(before, 3)}

                        return revenue_dict
                    # 2014년 보고서 디렉토리가 없으므로 2015년도 보고서의 year_before 칼럼에 속하는 2013년도의 비율은 계산할수 없다.
                    else:
                        revenue_dict = {year: round(curr, 3),
                                        year - 1: round(last, 3),
                                        year - 2: 0.0}
                        return revenue_dict
                except:
                    # logging.error(traceback.format_exc())
                    assets_dict = {year: 0.0,
                                   year - 1: 0.0,
                                   year - 2: 0.0
                                   }
                    return assets_dict

            # 총자산증가율 -확인
            def asset_growth_rate():
                # (금년도 자산총계 - 전년도 자산총계) / 전년도 자산총계 * 100
                try:
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

                        assets_dict = {year: round(curr, 3),
                                       year - 1: round(last, 3),
                                       year - 2: round(before, 3)}

                        return assets_dict
                    # 2014년 보고서 디렉토리가 없으므로 2015년도 보고서의 year_before 칼럼에 속하는 2013년도의 비율은 계산할수 없다.
                    else:
                        assets_dict = {year: round(curr, 3),
                                       year - 1: round(last, 3),
                                       year - 2: 0.0
                                       }
                        return assets_dict
                except:
                    assets_dict = {year: 0.0,
                                   year - 1: 0.0,
                                   year - 2: 0.0
                                   }
                    return assets_dict

            # 순이익 증가율(지배기업지분이 있을경우 지배기업지분으로 계산) -확인
            def net_profit_growth_rate():
                # (금년도 당기순이익 - 전년도 당기순이익) / 전년도 당기순이익 * 100
                try:
                    net_profit = self.select_net_profit(code, year)  # 당기순이익 셀렉터 함수 호출

                    curr_year = net_profit.get('curr_year')
                    last_year = net_profit.get('last_year')
                    year_before = net_profit.get('year_before')
                    before_last = net_profit.get('before_last')

                    curr = self.cal_increase_rate(curr_year, last_year)
                    last = self.cal_increase_rate(last_year, year_before)
                    before = self.cal_increase_rate(year_before, before_last)

                    owner_net_profit_dict = {
                        year: round(curr, 3),
                        year - 1: round(last, 3),
                        year - 2: round(before, 3)}
                    return owner_net_profit_dict

                # 데이터가 없는 경우
                except:
                    # logging.error(traceback.format_exc())
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
                    net_profit = self.select_net_profit(code, year)  # 당기순이익 셀렉터 함수 호출
                    net_profit = net_profit.get(quarter_str_list)  # 당기순이익

                    result = net_profit / assets * 100
                    return round(result, 3)
                except:
                    # logging.error(traceback.format_exc())
                    return 0.0

            # 매출액총이익률 -확인
            def gross_margin():
                # 매출액총이익 / 영업수익(매출액) * 100
                # 이익 : 얼마를 벌어서 얼마를 쓰고 남은 돈이 얼마인가?
                # 수익 : 얼마나 벌어들였냐
                # 매출총이익과 영업이익은 기업 가치 측면에서 중요함
                try:
                    result = gross_profit / revenue * 100
                    return round(result, 3)
                except:
                    return 0.0

            # <기업가치 관련 지수>
            # 자기자본이익률 -확인
            def roe():
                # 당기순이익 / 자기자본 * 100 -확인
                # 당기순이익 = 일정기간 동안에 기업이 창출한 순이익
                try:
                    net_profit = self.select_net_profit(code, year)  # 당기순이익 셀렉터 함수 호출
                    net_profit = net_profit.get(quarter_str_list)  # 당기순이익

                    result = net_profit / equity * 100
                    return round(result, 3)
                except:
                    # logging.error(traceback.format_exc())
                    return 0.0

            # 총자산회전율 -확인
            def asset_turnover():
                # 영업수익(매출) / 자산총계 * 100
                try:
                    result = revenue / assets * 100
                    return round(result, 3)
                except:
                    return 0.0

            result_dict = {
                'year': quarter_year,
                'code': code,
                'current_asset': current_asset_cal(),
                'total_sales': total_sales_cal(),
                'net_profit': profit,
                'operating_profit': operating_profit,
                'current_ratio': current_ratio(),
                'debt_ratio': debt_ratio(),
                'quick_ratio': quick_ratio(),
                'bis': bis(),
                'sales_growth_rate': sales_growth_rate().get(quarter_year),
                'asset_growth_rate': asset_growth_rate().get(quarter_year),
                'net_profit_growth_rate': net_profit_growth_rate().get(quarter_year),
                'roa': roa(),
                'roe': roe(),
                'eps': eps,
                'gross_margin': gross_margin(),
                'asset_turnover': asset_turnover()
            }

            return result_dict
        except:
            pass
            # logging.error(traceback.format_exc())

    # 재무비율 업데이트 : 메인
    def update_ratio(self, code, year):
        try:
            # 각 기업마다 2013~20nn 년까지 1년씩의 비율 계산값을 리턴
            quarter_str_list = ['curr_year', 'last_year', 'year_before']  # 각 분기별 값 추출하기 위한 변수
            quarter_diff_dict = {'curr_year': 0, 'last_year': 1, 'year_before': 2}  # 분기별 연도 계산하기 위한 변수
            quarter_count = len(quarter_str_list)
            tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')

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
            if year > 2015:
                quarter_count = 1
                quarter_str_list = ['curr_year']

            # 분기 년도 순회
            for position in range(quarter_count):
                diff = quarter_diff_dict.get(quarter_str_list[position])
                quarter_year = year - diff  # 분기 년도 계산
                result = self.cal_ratio(code, year, quarter_year, quarter_str_list[position])

                current_asset = result.get('current_asset')
                total_sales = result.get('total_sales')
                net_profit = result.get('net_profit')
                operating_profit = result.get('operating_profit')
                current_ratio = result.get('current_ratio')
                debt_ratio = result.get('debt_ratio')
                quick_ratio = result.get('quick_ratio')
                bis = result.get('bis')
                sales_growth_rate = result.get('sales_growth_rate')
                asset_growth_rate = result.get('asset_growth_rate')
                net_profit_growth_rate = result.get('net_profit_growth_rate')
                eps = result.get('eps')
                roa = result.get('roa')
                gross_margin = result.get('gross_margin')
                roe = result.get('roe')
                asset_turnover = result.get('asset_turnover')

                with self.conn.cursor() as curs:
                    # pbr, per, bps 는 연간 정기 업데이트에서 제외 : 수시로 업데이트 해야하기 때문에 StatesFrequencyUpdater 클래스에서 처리
                    # update 는 업데이트 날짜에 맞쳐서 자동생성
                    sql = f"REPLACE INTO company_state (code, year, sec, sec_nm, company_nm, rp_type, mk, last_update, " \
                          f"current_asset, total_sales, net_profit, operating_profit, " \
                          f"current_ratio, debt_ratio, quick_ratio, bis, " \
                          f"sales_growth_rate, asset_growth_rate, net_profit_growth_rate, " \
                          f"eps, roa, gross_margin, " \
                          f"roe, asset_turnover) " \
                          f"VALUES ('{code}', '{quarter_year}', '{sec_code}', '{sec_nm}', '{comp_nm}', '{state_rp_type}', '{mk}', '{tmnow}', " \
                          f"'{current_asset}', '{total_sales}', '{net_profit}', '{operating_profit}', " \
                          f"'{current_ratio}', '{debt_ratio}', '{quick_ratio}', '{bis}', " \
                          f"'{sales_growth_rate}', '{asset_growth_rate}', '{net_profit_growth_rate}', " \
                          f"'{eps}', '{roa}', '{gross_margin}', " \
                          f"'{roe}', '{asset_turnover}')"
                    curs.execute(sql)
                    self.conn.commit()
        except:
            logging.error(traceback.format_exc())
            return


if __name__ == '__main__':
    execution = StatesUpdater()

# 나야 각 지표들을 어느정도 공부했으니까 무엇을 의미하는지 조금은 안다고 할 수 있다. 하지만 일반인 입장에서 공부없이는 알기 힘들다
# 그리고 분석은 공부를 했어도 누구든 힘든 부분이다. 이걸 일반인들도, 공부했는데 잊어먹은 사람들도 알아먹기 쉽게 만들고 싶다.
import csv

import OpenDartReader
import FinanceDataReader as fdr
import pandas as pd
import traceback
import logging
from datetime import datetime
import time

pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)


# 매일 실행될 필요가 없고 기업실적, 재무제표가 업데이트 되는 분기에만 실행하면 된다.
# 기업보고서 다운로드 자동화 미구현
# 로그 기록시 기존 파일이 있다면 그 파일을 덮어씌우고 작성하거나 파일이름을 날짜로 구분하여 새로 만들도록 해야한다.
# db 입력시 날짜 칼럼 구분은 set_base_date 를 기준으로 계산한다.
class StateReader:
    # 재무, 실적 딕셔너리를 하나로 합쳐서? StateUpdater 클래스에 전달해주는 메서드 필요?
    # 알아볼수 있게 주석처리
    # 보고서에 없거나 구하지 못한 항목을 다른 방법으로 어떻게 취득할것인지 구상하기
    # 재무제표 연결,별도 구분 저장
    # DB Table 재검토및 수정
    # DB 테이블 생성 에러 공부

    def __init__(self):
        print('StateReader start...')
        test_list = ['000020', '000040', '000050', '000070', '000060', '000050', '000080']

        # dart access key
        api_key = '1df1a3c433cb50c187e45bb35461f17a5c28f255'
        dart = OpenDartReader(api_key)

        krx = self.read_krx_code()
        self.krx_count = len(krx)

        # 항목값의 분기
        self.curr_year = 'curr_year'  # 당기
        self.last_year = 'last_year'  # 전기
        self.year_before = 'year_before'  # 전전기

        # 보고서 타입
        self.FIRST_QUARTER = 11013
        self.HALF_QUARTER = 110123
        self.THIRD_QUARTER = 11014
        self.REPORT_CODE = 11011  # 연간 보고서

        # csv 인코딩 타입 분류
        self.ENCODING_SET_EUC_KR = 'euc-kr'
        self.ENCODING_SET_CP = 'cp949'

        # 보고서 자동 조회용 date 객체, 현재년도-1 기준
        self.year = format(datetime.today().year - 1)
        self.month = format(datetime.today().month)
        self.date = format(datetime.today().day)

        # 개인 : 일 10,000건 (서비스별 한도가 아닌 오픈 API 23종 전체 서비스 기준)
        # 일일한도를 준수하더라도 서비스의 안정적인 운영을 위하여 과도한 네트워크 접속(분당 100회 이상)은 서비스 이용이 제한
        for idx in range(self.krx_count):
            if (idx + 1) % 100 != 0:
                code = krx['code'].iloc[idx]
                # code = test_list[idx]
                self.small = dart.report(krx.code.values[idx], '소액주주', self.year, reprt_code=self.REPORT_CODE)

                self.financial_state_yearly(code)
                self.income_state_yearly(code)

                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                print(f"[{tmnow}] {idx + 1 :04d} / {len(krx)} code: {code} (READING REPORT)")
            else:
                time.sleep(62)

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
    def get_stock_price(code: str, start_year, end_year):
        df = fdr.DataReader(code, start_year)
        print(df.head(10))

    def convert_dataframe(self, report_dir: str, code: str):
        try:
            df = pd.read_csv(report_dir, sep='\t', engine='python', encoding=self.ENCODING_SET_CP)

            # 현재 분류 안되고 있음
            # if UnicodeEncodeError in df:
            #     df = pd.read_csv(report_dir, sep='\t', engine='python', encoding=self.ENCODING_SET_EUC_KR)

            # 데이터 가공 처리
            unnamed_position = df.columns[df.columns.str.contains('Unnamed: ')]  # Unnamed: num 제거 (공백 columns)
            df.drop(columns=unnamed_position, axis=0, inplace=True)
            df.drop(columns=["결산월", "보고서종류", "통화"], axis=1, inplace=True)
            # df.dropna(thresh=3, inplace=True)  # 결측치 포함된 행 자체가 제거된다, 3개 이상이 결측치라면 행 삭제
            df.fillna(0, inplace=True)  # 결측치를 전부 0으로 바꾼다.

            # 항목 필터링을 위해 칼럼 작업 필요 : 필요없는 칼럼을 지운다면 필터링 처리속도가 올라가지 않을까?
            # 필요없는 칼럼 : 결산월, 보고서종류, 통화
            df = df.rename(
                {'재무제표종류': 'type', '종목코드': 'code', '회사명': 'comp_name', '시장구분': 'mk', '업종': 'sec', '업종명': 'sec_nm',
                 '결산기준일': 'set_base_date', '항목코드': 'account_id', '항목명': 'account_nm', '당기': 'curr_year',
                 '전기': 'last_year', '전전기': 'year_before'}, axis='columns')

            # 종목 코드를 기준으로 각 항목 데이터 뽑아내기, Empty DataFrame일 경우 예외처리
            income_dataframe = df[df['code'] == f'[{code}]']  # type dataframe
            income_dataframe = income_dataframe.applymap(lambda x: str(x).lstrip())

            return income_dataframe
        except:
            logging.error(traceback.format_exc())

    def check_income_state(self, code: str):
        try:
            # 연결 손익계산서
            coverage_link_dir = 'krx_report/2020/year/income_state/2020_사업보고서_03_포괄손익계산서_연결_20210424.txt'
            normal_link_dir = 'krx_report/2020/year/income_state/2020_사업보고서_02_손익계산서_연결_20210424.txt'
            coverage_link_df = self.convert_dataframe(coverage_link_dir, code)
            normal_link_df = self.convert_dataframe(normal_link_dir, code)

            # 일반 손익계산서
            coverage_dir = 'krx_report/2020/year/income_state/2020_사업보고서_03_포괄손익계산서_20210424.txt'
            normal_dir = 'krx_report/2020/year/income_state/2020_사업보고서_02_손익계산서_20210424.txt'
            coverage_df = self.convert_dataframe(coverage_dir, code)
            normal_df = self.convert_dataframe(normal_dir, code)

            # 두 계산서를 합쳤을때 문제점 : 같은 항목명이 있을때 필터링 실패 확률이 높아진다.
            concat_report = pd.concat([coverage_df, normal_df, coverage_link_df, normal_link_df])
            if len(concat_report) > 0:
                return concat_report
            else:
                #  이보다 더 좋은 리턴값 생각해보자
                return 0
        except:
            logging.error(traceback.format_exc())

    def check_financial_state(self, code: str):
        try:
            # 연결 재무상태 보고서
            fin_state_link_dir = 'krx_report/2020/year/fin_state/2020_사업보고서_01_재무상태표_연결_20210424.txt'
            fin_state_link_df = self.convert_dataframe(fin_state_link_dir, code)

            # 일반 재무상태 보고서
            fin_state_dir = 'krx_report/2020/year/fin_state/2020_사업보고서_01_재무상태표_20210424.txt'
            fin_state_df = self.convert_dataframe(fin_state_dir, code)

            concat_report = pd.concat([fin_state_link_df, fin_state_df])

            if len(concat_report) > 0:
                return concat_report
            else:
                return 0
        except:
            logging.error(traceback.format_exc())

    # 연간 손익보고서
    def income_state_yearly(self, code):
        # 항목 수집률도 같이 표기하면 어떨까?
        try:
            # code = self.code
            # 0을 리턴 받았을경우 : 해당 회사 코드가 보고서에 없음. 예외처리 구상하기
            # 재무제표 종류: 연결, 별도 구분
            # print(rp_type)
            # if rp_type.str.contains('별도재무제표'):
            #     rp_type = '별도'
            # elif rp_type.str.contains('연결재무제표'):
            #     rp_type = '연결'
            #
            # print(rp_type)

            # 따로 함수를 만들어서 리턴해줄까? 손익/재무만 분류시켜줄수 있으면 된다. flag 인자를 줘서 말이야
            comp_state = self.check_income_state(code)
            # print(comp_state)
            rp_type = comp_state['type'].values[0]

            company_name = comp_state['comp_name'].values[0]  # 회사명
            set_base_date = comp_state['set_base_date'].values[0]  # 결산기준일
            sec = comp_state['sec'].values[0]  # 업종코드
            sec_nm = comp_state['sec_nm'].values[0]  # 업종명
            mk = comp_state['mk'].values[0]  # 시장구분

            success_log_dir = 'log/stateReader/income_success.txt'
            filed_log_dir = 'log/stateReader/income_filed.txt'

            curr_year = self.curr_year  # 당기
            last_year = self.last_year  # 전기
            year_before = self.year_before  # 전전기

            # account_nm으로 찾는거 보다 account_id로 찾는게 더 정확하다. (언어표기 다양성을 피할수 있다.) => 꼭그렇지만도 않다
            # 취득성공한 항목의 account_id도 제대로 취득한건지 기록해야함
            # 항목 필터링 함수
            def income_filtering(query_str: str, comp_code: str, target_nm: str, comp_nm: str):
                global key, account_nm
                try:
                    # key : 해당 항목을 필터링하는데 필요한 account_id, 쿼리문으로 특정, 쿼리문을 사용하면 프로그램 전체 처리속도가 떨어진다.
                    # 각 칼럼을 기준으로 필터링된 첫번째 값을 구한다. (내가 지금 생각해봐도 기적의 논리로 작동한다.)
                    key = comp_state.query(query_str)['account_id'].values[0]
                    account_nm = comp_state.query(query_str)['account_nm'].values[0]

                    # 당기, 전기, 전전기 항목 금액 : nan에 대한 예외처리 필요
                    curr_val = comp_state.loc[comp_state['account_id'].isin([key]), curr_year].values[0].replace(",", "")
                    last_val = comp_state.loc[comp_state['account_id'].isin([key]), last_year].values[0].replace(",", "")
                    before_val = comp_state.loc[comp_state['account_id'].isin([key]), year_before].values[0].replace(",", "")

                    curr_val = int(curr_val)
                    last_val = int(last_val)
                    before_val = int(before_val)

                    success_dict = {'code': comp_code,
                                    'comp_nm': comp_nm,
                                    'account_nm': account_nm,
                                    'type': rp_type,
                                    'target_nm': target_nm,
                                    'curr_year': curr_val,
                                    'last_year': last_val,
                                    'year_before': before_val}
                    with open(success_log_dir, mode='a', newline='') as file_success_log:
                        # 로그작성 필드네임은 기준이 되는 dict의 필드네임수, 이름과 일치해야 제대로 작성됨(이름이 틀릴경우 에러 발생)
                        writer = csv.DictWriter(file_success_log, fieldnames=['code', 'comp_nm', 'account_nm', 'type', 'target_nm', 'curr_year', 'last_year', 'year_before'])
                        writer.writerow(success_dict)
                    return success_dict

                except:
                    filed_dict = {'code': comp_code,
                                  'comp_nm': comp_nm,
                                  'target_nm': target_nm,
                                  'type': rp_type,
                                  'curr_year': 0,
                                  'last_year': 0,
                                  'year_before': 0}

                    with open(filed_log_dir, mode='a', newline='') as file_filed_log:
                        writer = csv.DictWriter(file_filed_log, fieldnames=['code', 'comp_nm', 'target_nm', 'type', 'curr_year', 'last_year', 'year_before'])
                        writer.writerow(filed_dict)
                        print('<손익 항목 취득실패>')
                        # print(str(logging.error(traceback.format_exc())))
                    return filed_dict

            # 각 항목 코드의 요구사항 : 필터링 키값, 항목값 취득 실패시 0과 해당 기업코드 리턴, 정규화된 항목명 리턴
            # 매출액
            def revenue():
                query_str = "(account_id == 'ifrs-full_Revenue') " \
                            "or (account_nm == '영업수익') " \
                            "or (account_nm == '수익(매출액)')" \
                            "or (account_nm == '매출액')"
                return income_filtering(query_str, code, '매출액', company_name)

            # 당기순이익 or 당기순이익(손실)
            def net_income():
                query_str = "(account_id == 'ifrs-full_ProfitLoss') or (account_nm == '당기순이익') or (account_nm == '당기손익') or " \
                            "(account_nm == '당기순이익(손실)')"
                return income_filtering(query_str, code, '당기순이익', company_name)

            # 주당손익
            def basic_earnings_loss_per_share():
                query_str = "(account_id == 'ifrs-full_BasicEarningsLossPerShareFromContinuingOperations') " \
                            "or (account_id == 'ifrs-full_BasicEarningsLossPerShare')" \
                            "or (account_nm == '보통주 기본및희석주당손익 (단위 : 원)') " \
                            "or (account_nm == '보통주의 기본주당순이익') " \
                            "or (account_nm == '보통주기본주당순이익') " \
                            "or (account_nm == '주당손익') " \
                            "or (account_nm == '주당이익') " \
                            "or (account_nm == '기본주당이익') " \
                            "or (account_nm == '기본주당손익') " \
                            "or (account_nm == '기본주당이익 및 희석주당이익')" \
                            "or (account_nm == '1. 기본주당순이익(손실)')" \
                            "or (account_nm == '기본 및 희석주당이익')"
                return income_filtering(query_str, code, '주당손익', company_name)

            # 금융수익
            def financial_income():
                query_str = "(account_id == 'ifrs-full_FinanceIncome') or (account_nm == '금융수익') " \
                            "or (account_nm == '금융손익') " \
                            "or (account_nm == '순금융수익(원가)') " \
                            "or (account_nm == '1. 금융수익')"
                return income_filtering(query_str, code, '금융수익', company_name)

            # 금융비용
            def finance_cost():
                query_str = "(account_id == 'ifrs-full_FinanceCosts') " \
                            "or (account_nm == '금융비용') " \
                            "or (account_nm == '금융원가')" \
                            "or (account_nm == '2. 금융비용')"
                return income_filtering(query_str, code, '금융비용', company_name)

            # 영업비용
            def cost_of_sales():
                query_str = "(account_id == 'dart_TotalSellingGeneralAdministrativeExpenses') or (account_nm == '영업비용') or" \
                            " (account_id == 'ifrs-full_CostOfSales')"
                return income_filtering(query_str, code, '영업비용', company_name)

            # 영업외손익 or 기타손익 or 기타포괄손익
            def non_oper_income():
                query_str = "(account_id == 'dart_OtherGains') or (account_id == 'ifrs-full_OtherComprehensiveIncome') or (account_nm == '영업외손익') or " \
                            "(account_nm == '기타포괄손익') or (account_nm == '기타손익')"
                return income_filtering(query_str, code, '영업외손익', company_name)

            # 영업외비용
            def non_oper_expenses():
                query_str = "(account_id == 'dart_OtherLosses') or (account_nm == '영업외비용') or (account_nm == '기타영업외비용')"
                return income_filtering(query_str, code, '영업외비용', company_name)

            # 법인세비용
            def corporate_tax():
                query_str = "(account_id == 'ifrs-full_IncomeTaxExpenseContinuingOperations') " \
                            "or (account_nm == '법인세비용')"
                return income_filtering(query_str, code, '법인세비용', company_name)

            # 데이터베이스에서 만큼은 항목명을 통일시켜서 넣어야 한다. 테이블도 전체 재검토하고 수정해야겠다.
            # 이걸 합칠거라면 칼럼이 중복되는건 한쪽에만 있어도 되지 않나?
            # 재무상태/ 손익계산서로 나뉜 항목 칼럼을 만들거라면 이 딕셔너리에 항목리턴 딕셔너리 전체를 리턴, 항목 칼럼 업데이터 필요
            income_report_dict = {'code': code,
                                  'company_name': company_name,
                                  'set_base_date': set_base_date,
                                  'sec': sec,
                                  'sec_nm': sec_nm,
                                  'mk': mk,
                                  'revenue': revenue().get('curr_year'),
                                  'net_income': net_income().get('curr_year'),
                                  'fin_income': financial_income().get('curr_year'),
                                  'fin_costs': finance_cost().get('curr_year'),
                                  'basic_per_share': basic_earnings_loss_per_share().get('curr_year'),
                                  'cost_of_sales': cost_of_sales().get('curr_year'),
                                  'non_oper_income': non_oper_income().get('curr_year'),
                                  'non_oper_expenses': non_oper_expenses().get('curr_year'),
                                  'corporate_tax': corporate_tax().get('curr_year')}

            # 코드리스트를 받게 될경우 분기 리턴 처리
            # 항목 취득 실패시 에러로그에 기록 분기 리턴 처리?
            # 너무 많은 기능이 한 함수에 몰려있는거 같다.
            return income_report_dict  # 재무상태 보고서랑 합쳐야 하기 때문에 데이터 프레임이 아닌 상대적으로 가벼운 dict 형태로 리턴한다.
        except:
            print(f'<손익 보고서에서 기업코드 [{code}] 를 읽을수가 없습니다. 로그를 확인하세요>')
            # print(str(logging.error(traceback.format_exc())))
            with open('log/stateReader/no_code_income.txt', mode='a') as f:
                f.write('' + code + '\n')

    # 연간 재무보고서 :
    def financial_state_yearly(self, code):  # year : 2020 => 2019
        try:
            # 전체 디렉토리를 자동으로 순환할수 있도록 해야한다.
            # code = self.code
            # 0을 리턴 받았을경우 : 해당 회사 코드가 보고서에 없음. 예외처리 구상하기
            comp_state = self.check_financial_state(code)

            # 뭐 하나만 에러가 나서 잘못되도 예외처리로 보고서에 코드가 있어도 없다고 해버리는 문제가 있다.
            # 이건 실적/재무에 중복으로 포함되는 값들이다.
            # 60에러후 70을 읽을수가 없다. 왜지?
            rp_type = comp_state['type'].values[0]  # 보고서 타입

            company_name = comp_state['comp_name'].values[0]  # 회사명
            set_base_date = comp_state['set_base_date'].values[0]  # 결산기준일
            sec = comp_state['sec'].values[0]  # 업종코드
            sec_nm = comp_state['sec_nm'].values[0]  # 업종명
            mk = comp_state['mk'].values[0]  # 시장구분

            small = self.small

            curr_year = self.curr_year  # 당기
            last_year = self.last_year  # 전기
            year_before = self.year_before  # 전전기

            success_log_dir = 'log/stateReader/statements_success.txt'
            filed_log_dir = 'log/stateReader/statements_filed.txt'

            # 항목 필터링 함수
            def fin_filtering(query_str: str, comp_code: str, target_nm: str, comp_nm: str):
                global key, account_nm
                try:
                    key = comp_state.query(query_str)['account_id'].values[0]
                    account_nm = comp_state.query(query_str)['account_nm'].values[0]

                    curr_val = comp_state.loc[comp_state['account_id'].isin([key]), curr_year].values[0].replace(",", "")
                    last_val = comp_state.loc[comp_state['account_id'].isin([key]), last_year].values[0].replace(",", "")
                    before_val = comp_state.loc[comp_state['account_id'].isin([key]), year_before].values[0].replace(",", "")

                    curr_val = int(curr_val)
                    last_val = int(last_val)
                    before_val = int(before_val)

                    success_dict = {'code': comp_code,
                                    'comp_nm': comp_nm,
                                    'account_nm': account_nm,
                                    'type': rp_type,
                                    'target_nm': target_nm,
                                    'curr_year': curr_val,
                                    'last_year': last_val,
                                    'year_before': before_val}
                    with open(success_log_dir, mode='a', newline='') as file_success_log:
                        # 로그작성 필드네임은 기준이 되는 dict의 필드네임수, 이름과 일치해야 제대로 작성됨(이름이 틀릴경우 에러 발생)
                        writer = csv.DictWriter(file_success_log, fieldnames=['code', 'comp_nm', 'account_nm', 'target_nm', 'type', 'curr_year', 'last_year', 'year_before'])
                        writer.writerow(success_dict)
                    return success_dict

                except:
                    filed_dict = {'code': comp_code,
                                  'comp_nm': comp_nm,
                                  'target_nm': target_nm,
                                  'curr_year': 0,
                                  'last_year': 0,
                                  'year_before': 0}

                    with open(filed_log_dir, mode='a', newline='') as file_filed_log:
                        writer = csv.DictWriter(file_filed_log, fieldnames=['code', 'comp_nm', 'target_nm', 'curr_year', 'last_year', 'year_before'])
                        writer.writerow(filed_dict)
                        # print(str(logging.error(traceback.format_exc())))
                        print('<재무 항목 취득실패>')
                    return filed_dict

            # 자본총계
            def equity():
                query_str = "(account_id == 'ifrs-full_Equity') or (account_nm == '자본총계')"
                return fin_filtering(query_str, code, '자본총계', company_name)

            # 부채총계
            def liabilities():
                query_str = "(account_id == 'ifrs-full_Liabilities') or (account_nm == '부채총계')"
                return fin_filtering(query_str, code, '부채총계', company_name)

            # 유동부채
            def current_liabilities():
                query_str = "(account_id == 'ifrs-full_CurrentLiabilities') or (account_nm == '유동부채총계')"
                return fin_filtering(query_str, code, '유동부채', company_name)

            # 유동자산
            def current_assets():
                query_str = "(account_id == 'ifrs-full_CurrentAssets') or (account_nm == '유동자산')"
                return fin_filtering(query_str, code, '유동자산', company_name)

            # 재고자산
            def inventories():
                query_str = "(account_id == 'ifrs-full_Inventories') or (account_nm == '재고자산')"
                return fin_filtering(query_str, code, '재고자산', company_name)

            # 자산총계
            def assets():
                query_str = "(account_id == 'ifrs-full_Assets') or (account_nm == '자산총계')"
                return fin_filtering(query_str, code, '자산총계', company_name)

            # 총발행주식수 : 5번쨰 반복하면 어떤 값도 나오지 않음, 값이 얿을수도 있음 따라서 예외처리 필요
            def stock_total():
                try:
                    stock_total_number = small['stock_tot_co'].str.replace(',', '')
                    stock_total_number = int(stock_total_number)
                    return stock_total_number
                except:
                    return 0

            fin_report_dict = {'code': code,
                               'comp_name': company_name,
                               'set_base_date': set_base_date,
                               'sec': sec,
                               'sec_nm': sec_nm,
                               'mk': mk,
                               'equity': equity().get('curr_year'),
                               'liabilities': liabilities().get('curr_year'),
                               'curr_liabilities': current_liabilities().get('curr_year'),
                               'curr_assets': current_assets().get('curr_year'),
                               'inventories': inventories().get('curr_year'),
                               'assets': assets().get('curr_year'),
                               'stock_total_number': stock_total()}

            return fin_report_dict
        except:
            print(f'<재무 보고서에서 기업코드 [{code}] 를 읽을수가 없습니다. 로그를 확인하세요>')
            # print(str(logging.error(traceback.format_exc())))
            with open('log/stateReader/no_code_fin.txt', mode='a') as f:
                f.write('' + code + '\n')



# readState 에서 읽어드린 기업 실적을 DB에 업데이트한다.
class StateUpdater:
    def __init__(self):
        print('updater init')

    def update_statement(self):

        print('업데이터 개발중')


if __name__ == '__main__':
    # 실행할 클래스 객체화
    reader_execution = StateReader()
    # updater_execution = StateUpdater()

    # reader_execution.income_state_yearly()
    # reader_execution.financial_state_yearly()

    # updater_execution.Update_statement()
    # reader_execution.get_stock_price('005930', 2020, '')

# 나야 각 지표들을 어느정도 공부했으니까 무엇을 의미하는지 조금은 안다고 할 수 있다. 하지만 일반인 입장에서 공부없이는 알기 힘들다
# 그리고 분석은 공부를 했어도 누구든 힘든 부분이다. 이걸 일반인들도, 공부했는데 잊어먹은 사람들도 알아먹기 쉽게 만들고 싶다.

import OpenDartReader
import FinanceDataReader as fdr
import pandas as pd
import traceback
import logging
from datetime import datetime

# dart access key
api_key = '1df1a3c433cb50c187e45bb35461f17a5c28f255'
dart = OpenDartReader(api_key)

pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)

# 매일 실행될 필요가 없고 기업실적, 재무제표가 업데이트 되는 분기에만 실행하면 된다.
# 기업보고서 다운로드 자동화 미구현
class StateReader:

    def __init__(self):
        print('reader init')
        krx = self.read_krx_code()
        # account_nm을 수집할때는 2437개를 한번에 읽게 되면 배열차원이 늘어나서 유동적인 대응이 힘들다. 따라서 100개 단위로 읽어야함
        # read_count 라는 텍스트파일을 만들고 매번 krx 읽을때 마다 그 값을 읽어서 stack에 곱한다.
        self.krx_count = 1  # default 100
        stack = 0  # default stack = 100 * read_count
        self.fi_array = []
        self.code = '089470'  # 카카오 : 035720 삼성전자 : 005930

        # 보고서 타입
        self.FIRST_QUARTER = 11013
        self.HALF_QUARTER = 110123
        self.THIRD_QUARTER = 11014
        self.REPORT_CODE = 11011  # 연간 보고서

        # id, nm 분류
        self.ACCOUNT_ID = 'account_id'
        self.ACCOUNT_NM = 'account_nm'

        # csv 인코딩 타입 분류
        self.ENCODING_SET_EUC_KR = 'euc-kr'
        self.ENCODING_SET_CP = 'cp949'

        # 보고서 자동 조회용 date 객체, 현재년도-1 기준
        self.last_year = format(datetime.today().year - 1)
        self.month = format(datetime.today().month)
        self.date = format(datetime.today().day)

        self.small = dart.report(krx.code.values[0], '소액주주', self.last_year, reprt_code=self.REPORT_CODE)
        # 개인 : 일 10,000건 (서비스별 한도가 아닌 오픈API 23종 전체 서비스 기준)
        # 일일한도를 준수하더라도 서비스의 안정적인 운영을 위하여 과도한 네트워크 접속(분당 100회 이상)은 서비스 이용이 제한
        # for idx in range(self.krx_count):
        #     if (idx + 1) % 100 != 0:
        #         small = dart.report(krx.code.values[idx], '소액주주', last_year, reprt_code=REPORT_CODE)
        #         tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
        #         print(f"[{tmnow}] {idx + 1+stack:04d} / {len(krx)} (READING REPORT)")
        #     else:
        #         time.sleep(70)

    def read_krx_code(self):
        """KRX로부터 상장법인목록 파일을 읽어와서 데이터프레임으로 반환"""
        url = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
        krx = pd.read_html(url, header=0)[0]  # [0]을 붙임으로써 결괏값을 데이터프레임으로 받는다.
        krx = krx[['종목코드', '회사명']]  # 종목코드 칼럼과 회사명만 남긴다. 데이터프레임에 [[]]을 사용하면 특정 칼럼만 뽑아서 원하는 순서대로 재구성할 수 있다.
        krx = krx.rename(columns={'종목코드': 'code', '회사명': 'company'})  # 한글 칼럼명을 영문 칼럼명으로 변경
        krx.code = krx['code'].map(
            '{:06d}'.format)  # krx_list[0].종목코드 = krx_list[0].종목코드.map('{:06d}'.format) # 종목코드의 앞자리 0 보정 : {:06f}는 여석 자리 숫자 형식으로 표현하되 빈 앞 자리를 0으로 채우라는 뜻
        krx = krx.sort_values(by='code')  # 종목코드 칼럼의 값으로 정렬, 기본은 오름차순 정렬이며, ascending=False를 인수로 추가하면 내림차순으로 정렬된다.
        return krx

    def convert_dataframe_call(self, report_dir, code):
        try:
            # ac.loc[fs['account_nm'].str.contains('당기순이익') & ac['account_id'].str.contains('표준')] => 예외처리용으로 써야겠다.
            # 재무상태표 csv: 항목(유동자산, 당기순이익, 매출액 등등)
            df = pd.read_csv(report_dir, sep='\t', engine='python', encoding=self.ENCODING_SET_EUC_KR)
            if df is UnicodeEncodeError:
                df = pd.read_csv(report_dir, sep='\t', engine='python', encoding=self.ENCODING_SET_CP)

            # 데이터 가공 처리
            unnamed_position = df.columns[df.columns.str.contains('Unnamed: ')]  # Unnamed: num 제거 (공백 columns)
            df.drop(columns=unnamed_position, axis=0, inplace=True)
            df.dropna(inplace=True)

            df = df.rename(
                {'재무제표종류': 'fin_type', '종목코드': 'code', '회사명': 'comp_name', '시장구분': 'mk', '업종': 'sec', '업종명': 'sec_nm',
                 '결산월': 'set_month', '결산기준일': 'set_base_date',
                 '보고서종류': 'report_type', '통화': 'currency', '항목코드': 'account_id', '항목명': 'account_nm', '당기': 'curr_year',
                 '전기': 'last_year', '전전기': 'year_before'}, axis='columns')
            # 종목 코드를 기준으로 각 항목 데이터 뽑아내기, Empty DataFrame일 경우 예외처리
            income_dataframe = df[df['code'] == f'[{code}]']  # type dataframe
            income_dataframe = income_dataframe.applymap(lambda x: str(x).lstrip())

            return income_dataframe
        except:
            logging.error(traceback.format_exc())

    def check_income_state(self, code):
        try:
            not_included_code = []
            coverage_report_dir = 'krx_all_report/2020/year/income_state/2020_사업보고서_03_포괄손익계산서_연결_20210424.txt'
            normal_report_dir = 'krx_all_report/2020/year/income_state/2020_사업보고서_02_손익계산서_연결_20210424.txt'

            coverage_report = self.convert_dataframe_call(coverage_report_dir, code)
            normal_report = self.convert_dataframe_call(normal_report_dir, code)

            # 두 계산서를 그냥 합쳐버릴까? 합쳤는데 문자끼리 충돌이 일어나면 어떻하지?
            # 두 계산서를 합쳤을때 문제점 : 같은 항목명이 있을때 필터링 실패 확률이 높아진다.
            concat_report = pd.concat([coverage_report, normal_report])

            if len(concat_report) > 0:
                return concat_report
            else:
                return not_included_code.append(code)

        except:
            logging.error(traceback.format_exc())

    def check_financial_state(self, code):
        try:
            not_included_code = []
            fin_state_dir = 'krx_all_report/2020/year/fin_state/2020_사업보고서_01_재무상태표_연결_20210424.txt'

            coverage_report = self.convert_dataframe_call(fin_state_dir, code)

            if len(coverage_report) > 0:
                return coverage_report
            else:
                return not_included_code.append(code)

        except:
            logging.error(traceback.format_exc())

    def get_stock_price(self, code, start_year, end_year):
        df = fdr.DataReader(code, start_year)
        print(df.head(10))

    # 로그처리 : 1.코드없음(코드), 2.성공, 3.실패(코드, 회사이름, 취득한 account_id와 account_nm, target_nm) 로그 문서처리
    # financial_state_yearly 키값, 항목 추출 내부메소드, 딕셔너리 리턴작업
    # 재무, 실적 딕셔너리를 하나로 합쳐서 StateUpdater 클래스에 전달해주는 메서드 필요
    # 알아볼수 있게 주석처리

    # DB Table 재검토및 수정
    # DB 테이블 생성 에러 공부
    # 항목 업데이트 메서드 만들기

    def income_state_yearly(self):
        # 항목 수집률도 같이 표기하면 어떨까?
        try:
            code = self.code
            comp_state = self.check_income_state(self.code)
            company_name = comp_state['comp_name'].values[0]
            set_base_date = comp_state['set_base_date'].values[0]
            print(comp_state)

            # account_nm으로 찾는거 보다 account_id로 찾는게 더 정확하다. (언어표기 다양성을 피할수 있다.) => 꼭그렇지만도 않다
            # 취득성공한 항목의 account_id도 제대로 취득한건지 기록해야함

            # 각 항목 코드의 요구사항 : 필터링 키값, 항목값 취득 실패시 0과 해당 기업코드 리턴, 정규화된 항목명 리턴
            # 매출액
            def revenue():
                try:
                    key = comp_state.query(
                        "(account_id == 'ifrs-full_Revenue') or (account_nm == '영업수익') or (account_nm == '수익(매출액)')")[
                        'account_id'].values[0]  # type = str
                    value = comp_state.loc[comp_state['account_id'].isin([key]), 'curr_year'].values[0].replace(",",                                                                                     "")
                    value = int(value)  # type = 시리즈(str, replace 사용가능

                    success_dict = {'value': value, 'account_nm': '매출', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '매출',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 전기 매출액
            def last_revenue():
                try:
                    ket = comp_state.query(
                        "(account_id == 'ifrs-full_Revenue') or (account_nm == '영업수익') or (account_nm == '수익(매출액)')")[
                        'account_id'].values[0]  # type = str

                    value = comp_state.loc[comp_state['account_id'].isin([ket]), 'last_year'].values[0].replace(
                        ",", "")
                    value = int(value)
                    success_dict = {'value': value, 'account_nm': '전기 매출', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '전기 매출',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 당기순이익 or 당기순이익(손실)
            def net_income():
                try:
                    key = comp_state.query("(account_id == 'ifrs-full_ProfitLoss') or (account_nm == '당기순이익') or (account_nm == '당기손익') or"
                                           "(account_nm == '당기순이익(손실)')")['account_id'].values[0]
                    value = comp_state.loc[comp_state['account_id'].isin([key]), 'curr_year'].values[0].replace(",", "")
                    value = int(value)
                    success_dict = {'value': value, 'account_nm': '당기순이익', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '당기순이익',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 전기 당기순이익
            def last_net_income():
                try:
                    key = comp_state.query(
                        "(account_id == 'ifrs-full_ProfitLoss') or (account_nm == '당기순이익') or (account_nm == '당기손익') or"
                        "(account_nm == '당기순이익(손실)')")['account_id'].values[0]
                    value = comp_state.loc[comp_state['account_id'].isin([key]), 'last_year'].values[
                            0].replace(
                            ",", "")
                    value = int(value)
                    success_dict = {'value': value, 'account_nm': '전기 당기순이익', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '전기 당기순이익',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 주당손익
            def basic_earnings_loss_per_share():
                try:
                    key = comp_state.query(
                        "(account_id == 'ifrs-full_BasicEarningsLossPerShareFromContinuingOperations') or (account_id == 'ifrs-full_BasicEarningsLossPerShare')"
                        " or (account_nm == '주당손익') or (account_nm == '주당이익') or (account_nm == '기본주당이익') or (account_nm == '기본주당손익') or "
                        "(account_nm == '기본주당이익 및 희석주당이익')")['account_id'].values[0]
                    print('주당손익 키:' + key)
                    value = comp_state.loc[
                            comp_state['account_id'].isin([key]), 'curr_year'].values[
                            0].replace(",", "")
                    value = int(value)
                    success_dict = {'value': value, 'account_nm': '주당손익', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '주당손익',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 금융수익
            def financial_income():
                try:
                    key = comp_state.query(
                        "(account_id == 'ifrs-full_FinanceIncome') or (account_nm == '금융수익') or (account_nm == '금융손익')")[
                        'account_id'].values[0]
                    value = comp_state.loc[comp_state['account_id'].isin([key]), 'curr_year'].values[0].replace(",", "")
                    value = int(value)

                    success_dict = {'value': value, 'account_nm': '금융수익', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '금융수익',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 금융비용
            def finance_cost():
                try:
                    key = comp_state.query(
                        "(account_id == 'ifrs-full_FinanceCosts') or (account_nm == '금융비용') or (account_nm == '금융원가')")[
                        'account_id'].values[0]
                    value = comp_state.loc[comp_state['account_id'].isin([key]), 'curr_year'].values[0].replace(",", "")
                    value = int(value)

                    success_dict = {'value': value, 'account_nm': '금융비용', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '금융비용',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 영업비용
            def cost_of_sales():
                try:
                    key = comp_state.query(
                        "(account_id == 'dart_TotalSellingGeneralAdministrativeExpenses') or (account_nm == '영업비용') or"
                        " (account_id == 'ifrs-full_CostOfSales')")['account_id'].values[0]
                    value = comp_state.loc[comp_state['account_id'].isin(
                        [key]), 'curr_year'].values[0].replace(",", "")
                    value = int(value)

                    success_dict = {'value': value, 'account_nm': '영업비용', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '영업비용',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 영업외손익 or 기타손익 or 기타포괄손익
            def non_oper_income():
                try:
                    key = comp_state.query(
                        "(account_id == 'dart_OtherGains') or (account_id == 'ifrs-full_OtherComprehensiveIncome') or (account_nm == '영업외손익') or"
                        "(account_nm == '기타포괄손익') or (account_nm == '기타손익')")['account_id'].values[0]
                    value = comp_state.loc[comp_state['account_id'].isin([key]), 'curr_year'].values[0].replace(",", "")
                    value = int(value)

                    success_dict = {'value': value, 'account_nm': '영업외손익', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '영업외손익',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 영업외비용
            def non_oper_expenses():
                try:
                    key = comp_state.query(
                        "(account_id == 'dart_OtherLosses') or (account_nm == '영업외비용') or (account_nm == '기타영업외비용')")[
                        'account_id'].values[0]
                    value = comp_state.loc[comp_state['account_id'].isin([key]), 'curr_year'].values[0].replace(",", "")
                    value = int(value)

                    success_dict = {'value': value, 'account_nm': '영업외비용', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '영업외비용',
                                 'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict

            # 법인세비용
            def corporate_tax():
                try:
                    key = comp_state.query(
                        "(account_id == 'ifrs-full_IncomeTaxExpenseContinuingOperations') or (account_nm == '법인세비용')")[
                        'account_id'].values[0]
                    value = comp_state.loc[comp_state['account_id'].isin(
                        [key]), 'curr_year'].values[0].replace(",", "")
                    value = int(value)

                    success_dict = {'value': value, 'account_nm': '법인세비용', 'code': code}
                    return success_dict
                except:
                    logging.error(traceback.format_exc())
                    filed_dict = {'value': 0, 'account_nm': '법인세비용',
                                  'code': code}  # 에러로그에 기록해야 하기 때문에 일단 데이터 취득 성공,실패시 전부 dict 형태로 리턴
                    return filed_dict


            # 데이터베이스에서 만큼은 항목명을 통일시켜서 넣어야 한다. 테이블도 전체 재검토하고 수정해야겠다.
            income_report_dict = {'code': code, 'set_base_date': set_base_date,
                                  'company_name': company_name,
                                  'revenue': revenue().get('value'),
                                  'last_revenue': last_revenue().get('value'),
                                  'net_income': net_income().get('value'),
                                  'last_net_income': last_net_income().get('value'),
                                  'financial_income': financial_income().get('value'),
                                  'finance_costs': finance_cost().get('value'),
                                  'basic_earnings_loss_per_share': basic_earnings_loss_per_share().get('value'),
                                  'cost_of_sales': cost_of_sales().get('value'),
                                  'non_oper_income': non_oper_income().get('value'),
                                  'non_oper_expenses': non_oper_expenses().get('value'),
                                  'corporate_tax': corporate_tax().get('value')}

            # 코드리스트를 받게 될경우 분기 리턴 처리
            # 항목 취득 실패시 에러로그에 기록 분기 리턴 처리?
            # 너무 많은 기능이 한 함수에 몰려있는거 같다.
            print(income_report_dict)
            return income_report_dict  # 재무상태 보고서랑 합쳐야 하기 때문에 데이터 프레임이 아닌 상대적으로 가벼운 dict 형태로 리턴한다.
        except:
            logging.error(traceback.format_exc())
            #  최종 리턴 결과물을 각 기업재무당 데이터프레임으로 만들고 db에 전송하는 함수에 인자로 전달할까?

    def financial_state_yearly(self):  # year : 2020 => 2019
        try:
            # 전체 디렉토리를 자동으로 순환할수 있도록 해야한다.
            comp_state = self.check_financial_state(self.code)
            small = self.small

            # 자본총계
            equity = int(
                comp_state.loc[comp_state['account_id'].isin(['ifrs-full_Equity']), 'curr_year'].str.replace(",", ""))
            print(equity)
            # 전기 자본총계
            last_equity = int(
                comp_state.loc[comp_state['account_id'].isin(['ifrs-full_Equity']), 'last_year'].str.replace(",", ""))
            # 부채총계
            liabilities = int(
                comp_state.loc[comp_state['account_id'].isin(['ifrs-full_Liabilities']), 'curr_year'].str.replace(",",
                                                                                                                  ""))
            # 유동부채
            currentLiabilities = int(comp_state.loc[comp_state['account_id'].isin(
                ['ifrs-full_CurrentLiabilities']), 'curr_year'].str.replace(",", ""))

            # 전기 부채총계
            last_liabilities = int(comp_state.loc[comp_state['account_id'].isin(
                ['ifrs-full_CurrentLiabilities']), 'last_year'].str.replace(",", ""))

            # 유동자산
            currentAssets = int(
                comp_state.loc[comp_state['account_id'].isin(['ifrs-full_CurrentAssets']), 'curr_year'].str.replace(",",
                                                                                                                    ""))
            # 재고자산
            inventories = int(
                comp_state.loc[comp_state['account_id'].isin(['ifrs-full_Inventories']), 'curr_year'].str.replace(",",
                                                                                                                  ""))
            # 자산총계
            assets = int(
                comp_state.loc[comp_state['account_id'].isin(['ifrs-full_Assets']), 'curr_year'].str.replace(",", ""))

            stock_count = int(
                small['stock_tot_co'].str.replace(',', '')
            )  # 총발행주식수

        # dic = {'code', 'date', 'equity', 'last_equity', 'liabilities', 'currentLiabilities'
        #        'last_liabilities', 'currentAssets', 'inventories',
        #        'nonOperExpenses', 'corporateTax', assets}
        except AttributeError:
            logging.error(traceback.format_exc())
            pass
        except TypeError:
            logging.error(traceback.format_exc())
            pass



# readState에서 읽어드린 기업 실적을 DB에 업데이트한다.
class StateUpdater:
    def __init__(self):
        print('updater init')

    def Update_statement(self):

        # dic = {'code', 'date', 'equity', 'last_equity', 'liabilities', 'currentLiabilities'
        #        'last_liabilities', 'currentAssets', 'revenue', 'last_revenue', 'inventories', 'netIncome',
        #        'last_netIncome', 'operatingExpenses', 'financialIncome', 'financeCosts', 'nonOperExpenses',
        #        'corporateTax', asset}

        print('업데이터 개발중')


if __name__ == '__main__':
    # 실행할 클래스 객체화
    reader_execution = StateReader()
    updater_execution = StateUpdater()

    # reader_execution.income_state_yearly()
    reader_execution.financial_state_yearly()

    # updater_execution.Update_statement()
    # reader_execution.get_stock_price('005930', 2020, '')

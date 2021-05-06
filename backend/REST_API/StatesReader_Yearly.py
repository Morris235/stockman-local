# 나야 각 지표들을 어느정도 공부했으니까 무엇을 의미하는지 조금은 안다고 할 수 있다. 하지만 일반인 입장에서 공부없이는 알기 힘들다
# 그리고 분석은 공부를 했어도 누구든 힘든 부분이다. 이걸 일반인들도, 공부했는데 잊어먹은 사람들도 알아먹기 쉽게 만들고 싶다.
import os
import pandas as pd
import traceback
import logging
from datetime import datetime
import time
import csv

# 콘솔에 판다스 결과값 최대 표시 설정
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)


# 매일 실행될 필요가 없고 기업실적, 재무제표가 업데이트 되는 분기에만 실행하면 된다.(dart 에 보고서 업데이트 자동 감시 기능 필요)

# 기업보고서 다운로드 자동화 구현 필요
# 로그 기록시 기존 파일이 있다면 그 파일을 덮어씌우고 작성하거나 파일이름을 날짜로 구분하여 새로 만들도록 해야한다.
# db 입력시 날짜 칼럼 구분은 set_base_date 를 기준으로 계산한다.
# 디렉토리 생성, 구조화 설계 작업, 각 보고서 순회 방법 -> 2015~2020이상, year/2020_사업보고서_n_rp_nm_date.txt
class StateReader:
    def __init__(self):
        # global cash_txt, flu_txt

        print('StateReader Start')
        # krx 공시 전체 기업 코드 조회용
        krx = self.read_krx_code()
        krx_count = len(krx)

        # 디렉토리/파일 이름 리스트 : 연도별 보고서 순환
        txt_dic = self.read_file_list()
        self.year_list = txt_dic.get('year_list')
        self.fin_txt_list = txt_dic.get('fin_txt_list')
        self.income_txt_list = txt_dic.get('income_txt_list')
        # self.cash_txt_list = txt_dic.get('cash_txt_list')
        # self.flu_txt_list = txt_dic.get('flu_txt_list')

        self.fin_txt = ''
        self.income_txt = ''

        # 항목값의 분기
        self.curr_year = 'curr_year'  # 당기
        self.last_year = 'last_year'  # 전기
        self.year_before = 'year_before'  # 전전기

        # 전체 디렉토리 체크및 생성 순회
        # 순환구조 :
        # 디렉토리, 파일 순환 : state_all_report/ {년도:디렉토리}/ 분기:연간/ {file name: 재무,손익,+@}
        # 1.init 에서 전체 기업 코드를 모두 순환하면 루트에 해당년도 디렉토리 만들고(디렉토리가 있는 경우 건너띄기),
        # 2.다음 년도 디렉토리 선택후 전체 기업코드 순환
        for position in range(len(self.year_list)):
            check_dir = self.check_dir_name(self.year_list[position])
            year_dir = str(self.year_list[position])

            # 루트 디렉토리에 파일이 없다면 실행할 코드
            if check_dir:
                os.makedirs(f'refined_state_files/state_year/{str(self.year_list[position])}')
                self.fin_txt = self.fin_txt_list[position]
                self.income_txt = self.income_txt_list[position]

                # 개인 : 일 10,000건 (서비스별 한도가 아닌 오픈 API 23종 전체 서비스 기준)
                # 일일한도를 준수하더라도 서비스의 안정적인 운영을 위하여 과도한 네트워크 접속(분당 100회 이상)은 서비스 이용이 제한
                # 전체 krx 기업코드 순회
                for idx in range(krx_count):
                    if (idx + 1) % 100 != 0:
                        code = krx['code'].iloc[idx]  # krx 기업 code 조회

                        self.financial_state(code, year_dir)
                        self.income_state(code, year_dir)

                        tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                        print(f"[{tmnow}] {idx + 1 :04d} / {len(krx)} code: {code} (READING REPORT)")
                    else:
                        time.sleep(62)

            #  루트 디렉토리에 파일이 있다면 실행할 코드
            else:
                pass

    # krx 전종목 코드 리턴
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
    def read_file_list():
        # 재무상태표 2개, 손익계산서 4개, 현금흐름표 2개, 자본변동표 2개
        all_fin_txt_list = []
        all_income_txt_list = []
        all_cash_txt_list = []
        all_flu_txt_list = []

        # 디렉토리명에서 연도 얻기
        root_dir = 'state_all_report'
        year_list = os.listdir(root_dir)

        for year in year_list:
            path_dir = f'state_all_report/{year}/year'
            file_list = os.listdir(path_dir)

            all_fin_txt_list.append(file_list[0:2])
            all_income_txt_list.append(file_list[2:6])
            all_cash_txt_list.append(file_list[6:8])
            all_flu_txt_list.append(file_list[8:11])

        # txt_list 크기 = n년치 보고서 -> n개
        # 접근 = [0]=>년도 (0~n), [0][n]=>보고서
        txt_name_dict = {'fin_txt_list': all_fin_txt_list,
                         'income_txt_list': all_income_txt_list,
                         'cash_txt_list': all_cash_txt_list,
                         'flu_txt_list': all_flu_txt_list,
                         'year_list': year_list}
        return txt_name_dict

    # 손익/재무상태 보고서 데이터프레임 가공
    @staticmethod
    def convert_dataframe(report_dir: str, code: str):
        try:
            df = pd.read_csv(report_dir, sep='\t', engine='python', encoding='cp949')

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

            # 종목 코드를 기준으로 각 항목 데이터 뽑아내기, Empty DataFrame 일 경우 예외처리
            income_dataframe = df[df['code'] == f'[{code}]']  # type dataframe
            income_dataframe = income_dataframe.applymap(lambda x: str(x).lstrip())

            return income_dataframe
        except:
            logging.error(traceback.format_exc())

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

    # 연결/별도 손익 계산서 결합
    def concat_income_state(self, code: str, year_dir: str):
        try:
            # 연결 손익계산서
            coverage_link_dir = f'state_all_report/{year_dir}/year/{self.income_txt[3]}'
            normal_link_dir = f'state_all_report/{year_dir}/year/{self.income_txt[1]}'
            coverage_link_df = self.convert_dataframe(coverage_link_dir, code)
            normal_link_df = self.convert_dataframe(normal_link_dir, code)

            # 일반 손익계산서
            coverage_dir = f'state_all_report/{year_dir}/year/{self.income_txt[2]}'
            normal_dir = f'state_all_report/{year_dir}/year/{self.income_txt[0]}'
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

    # 연결/별도 재무상태 보고서 결합
    def concat_fin_state(self, code: str, year_dir: str):
        try:
            # 연결 재무상태 보고서
            link_dir = f'state_all_report/{year_dir}/year/{self.fin_txt[1]}'
            fin_state_link_df = self.convert_dataframe(link_dir, code)

            # 일반 재무상태 보고서
            normal_dir = f'state_all_report/{year_dir}/year/{self.fin_txt[0]}'
            fin_state_df = self.convert_dataframe(normal_dir, code)

            concat_report = pd.concat([fin_state_link_df, fin_state_df])

            if len(concat_report) > 0:
                return concat_report
            else:
                return 0
        except:
            logging.error(traceback.format_exc())

    # 연간 손익보고서
    def income_state(self, code: str, year_dir: str):
        # 항목 수집률도 같이 표기하면 어떨까?
        try:
            comp_state = self.concat_income_state(code, year_dir)

            rp_type = comp_state['type'].values[0]  # 보고서 타입
            company_name = comp_state['comp_name'].values[0]  # 회사명
            set_base_date = comp_state['set_base_date'].values[0]  # 결산기준일
            sec = comp_state['sec'].values[0]  # 업종코드
            sec_nm = comp_state['sec_nm'].values[0]  # 업종명
            mk = comp_state['mk'].values[0]  # 시장구분

            # 필터링된 항목 csv 파일 저장위치와 파일명
            success_log_dir = f'refined_state_files/state_year/{year_dir}/income_success.txt'
            filed_log_dir = f'refined_state_files/state_year/{year_dir}/income_filed.txt'

            curr_year = self.curr_year  # 당기
            last_year = self.last_year  # 전기
            year_before = self.year_before  # 전전기

            # 항목 필터링 함수
            def income_filtering(query_str: str, comp_code: str, target_nm: str, comp_nm: str):
                global key, account_nm
                try:
                    # key : 해당 항목을 필터링하는데 필요한 account_id, 쿼리문으로 특정, 쿼리문을 사용하면 프로그램 전체 처리속도가 떨어진다.
                    # 각 칼럼을 기준으로 필터링된 첫번째 값을 구한다. (내가 지금 생각해봐도 기적의 논리로 작동한다.)
                    key = comp_state.query(query_str)['account_id'].values[0]
                    account_nm = comp_state.query(query_str)['account_nm'].values[0]

                    # 당기, 전기, 전전기 항목 금액 : nan에 대한 예외처리 필요
                    curr_val = comp_state.loc[comp_state['account_id'].isin([key]), curr_year].values[0].replace(",",
                                                                                                                 "")
                    last_val = comp_state.loc[comp_state['account_id'].isin([key]), last_year].values[0].replace(",",
                                                                                                                 "")
                    before_val = comp_state.loc[comp_state['account_id'].isin([key]), year_before].values[0].replace(
                        ",", "")

                    curr_val = int(curr_val)
                    last_val = int(last_val)
                    before_val = int(before_val)

                    success_dict = {'code': comp_code,
                                    'comp_nm': comp_nm,
                                    'type': rp_type,
                                    'account_nm': account_nm,
                                    'target_nm': target_nm,
                                    'set_base_date': set_base_date,
                                    'sec': sec,
                                    'sec_nm': sec_nm,
                                    'mk': mk,
                                    'curr_year': curr_val,
                                    'last_year': last_val,
                                    'year_before': before_val}

                    # 필터링된 항목들 기록
                    with open(success_log_dir, mode='a', newline='') as file_success_log:
                        # 로그작성 필드네임은 기준이 되는 dict의 필드네임수, 이름과 일치해야 제대로 작성됨(이름이 틀릴경우 에러 발생)
                        writer = csv.DictWriter(file_success_log,
                                                fieldnames=['comp_nm', 'code', 'type', 'account_nm', 'target_nm',
                                                            'set_base_date', 'sec', 'sec_nm', 'mk',
                                                            'curr_year', 'last_year', 'year_before'])
                        writer.writerow(success_dict)
                    return success_dict
                except:
                    filed_dict = {'code': comp_code,
                                  'comp_nm': comp_nm,
                                  'target_nm': target_nm,
                                  'type': rp_type
                                  }

                    with open(filed_log_dir, mode='a', newline='') as file_filed_log:
                        writer = csv.DictWriter(file_filed_log,
                                                fieldnames=['comp_nm', 'code', 'target_nm', 'type'])
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

            # 필터링 함수를 실핼하기 위한 호출
            revenue()
            net_income()
            financial_income()
            finance_cost()
            basic_earnings_loss_per_share()
            cost_of_sales()
            non_oper_income()
            non_oper_expenses()
            corporate_tax()

            # 항목 취득에 성공한 코드리스트 기록
        except:
            print(f'<손익 보고서에서 기업코드 [{code}] 를 읽을수가 없습니다. 로그를 확인하세요>')
            # print(str(logging.error(traceback.format_exc())))
            with open(f'refined_state_files/state_year/{year_dir}/no_code_income.txt', mode='a') as f:
                f.write('' + code + '\n')

    # 연간 재무보고서 :
    def financial_state(self, code: str, year_dir: str):  # year : 2020 => 2019
        try:
            # 전체 디렉토리를 자동으로 순환할수 있도록 해야한다.
            comp_state = self.concat_fin_state(code, year_dir)

            # 뭐 하나만 에러가 나서 잘못되도 예외처리로 보고서에 코드가 있어도 없다고 해버리는 문제가 있다.
            rp_type = comp_state['type'].values[0]  # 보고서 타입
            company_name = comp_state['comp_name'].values[0]  # 회사명
            set_base_date = comp_state['set_base_date'].values[0]  # 결산기준일
            sec = comp_state['sec'].values[0]  # 업종코드
            sec_nm = comp_state['sec_nm'].values[0]  # 업종명
            mk = comp_state['mk'].values[0]  # 시장구분

            curr_year = self.curr_year  # 당기
            last_year = self.last_year  # 전기
            year_before = self.year_before  # 전전기

            success_log_dir = f'refined_state_files/state_year/{year_dir}/statements_success.txt'
            filed_log_dir = f'refined_state_files/state_year/{year_dir}/statements_filed.txt'
            include_coed_list_dir = f'refined_state_files/state_year/{year_dir}/state_code_list.txt'

            # 항목 필터링 함수
            def fin_filtering(query_str: str, comp_code: str, target_nm: str, comp_nm: str):
                global key, account_nm
                try:
                    key = comp_state.query(query_str)['account_id'].values[0]
                    account_nm = comp_state.query(query_str)['account_nm'].values[0]

                    curr_val = comp_state.loc[comp_state['account_id'].isin([key]), curr_year].values[0].replace(",",
                                                                                                                 "")
                    last_val = comp_state.loc[comp_state['account_id'].isin([key]), last_year].values[0].replace(",",
                                                                                                                 "")
                    before_val = comp_state.loc[comp_state['account_id'].isin([key]), year_before].values[0].replace(
                        ",", "")

                    curr_val = int(curr_val)
                    last_val = int(last_val)
                    before_val = int(before_val)

                    success_dict = {'comp_nm': comp_nm,
                                    'code': comp_code,
                                    'type': rp_type,
                                    'account_nm': account_nm,
                                    'target_nm': target_nm,
                                    'set_base_date': set_base_date,
                                    'sec': sec,
                                    'sec_nm': sec_nm,
                                    'mk': mk,
                                    'curr_year': curr_val,
                                    'last_year': last_val,
                                    'year_before': before_val,
                                    }

                    with open(success_log_dir, mode='a', newline='') as file_success_log:
                        # 로그작성 필드네임은 기준이 되는 dict의 필드네임수, 이름과 일치해야 제대로 작성됨(이름이 틀릴경우 에러 발생)
                        writer = csv.DictWriter(file_success_log,
                                                fieldnames=['comp_nm', 'code', 'type', 'account_nm', 'target_nm',
                                                            'set_base_date', 'sec', 'sec_nm', 'mk',
                                                            'curr_year', 'last_year', 'year_before'])
                        writer.writerow(success_dict)
                    return success_dict

                except:
                    filed_dict = {'comp_nm': comp_nm,
                                  'code': comp_code,
                                  'target_nm': target_nm}

                    with open(filed_log_dir, mode='a', newline='') as file_filed_log:
                        writer = csv.DictWriter(file_filed_log,
                                                fieldnames=['comp_nm', 'code', 'target_nm'])
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

            # 필터링 함수를 실핼하기 위한 호출
            equity()
            liabilities()
            current_liabilities()
            current_assets()
            inventories()
            assets()

            # 항목 취득에 성공한 코드리스트 기록
            with open(include_coed_list_dir, mode='a') as c:
                c.write('' + code + '\n')
        except:
            print(f'<재무 보고서에서 기업코드 [{code}] 를 읽을수가 없습니다. 로그를 확인하세요>')
            # print(str(logging.error(traceback.format_exc())))
            with open(f'refined_state_files/state_year/{year_dir}/no_code.txt', mode='a') as f:
                f.write('' + code + '\n')


if __name__ == '__main__':
    # 실행할 클래스 객체화
    execution = StateReader()

# 종목코드 순회중 가장 최근연도를 기준으로 테이블에서 상호명, 업종코드, 업종명을 통일
import traceback
import os
import pandas as pd
import logging
from REST_API.DB.Connector import connector
# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)

# 콘솔에 판다스 결과값 최대 표시 설정
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)


class StatesModifyUpdater:
    def __init__(self):
        print('Company State Modifying')
        recent_year = self.recent_report_year()
        self.modify_update(recent_year)

    # 가장 최근 refined dir 조회
    @staticmethod
    def recent_report_year():
        root_dir = 'refined_state_files/year'
        root_file_list = os.listdir(root_dir)
        last_dir = root_file_list[-1]
        return last_dir

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

    # 같은 종목 코드를 가진 기업명을 최근 연도 기준으로 통일
    def modify_update(self, recent_year):
        try:
            with connector.cursor() as curs:
                # 해당 종목코드칼럼, year칼럼에서 가장 큰 숫자를 기준
                sql = f"SELECT year, code FROM company_state WHERE year={recent_year};"
                df = pd.read_sql(sql, connector)

                # 최근 연도를 기준으로 상호명 조회및 데이터프레임화
                for code in df.code:
                    sql = f"SELECT code, company_nm, sec, sec_nm FROM company_state WHERE code={code};"
                    df = pd.read_sql(sql, connector)
                    recent_comp_nm = df.company_nm.iloc[-1]
                    recent_sec = df.sec.iloc[-1]
                    recent_sec_nm = df.sec_nm.iloc[-1]

                    # 변경된 상호명으로 업데이트. 업종코드, 업종명
                    sql = f"UPDATE company_state SET company_nm='{recent_comp_nm}', sec='{recent_sec}', sec_nm='{recent_sec_nm}'" \
                          f"WHERE code='{code}';"
                    curs.execute(sql)
                    connector.commit()
                    print(f"code: {code}, comp_nm: {recent_comp_nm}, sec: {recent_sec}, sec_nm: {recent_sec_nm}")
        except:
            logging.error(traceback.format_exc())
            return

    # 상장 폐지된 종목 row 삭제


if __name__ == '__main__':
    execution = StatesModifyUpdater()

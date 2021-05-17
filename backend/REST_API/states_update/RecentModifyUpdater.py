# 종목코드 순회중 가장 최근연도를 기준으로 테이블에서 상호명, 업종코드, 업종명을 통일
import traceback

import pymysql
import os
import pandas as pd
import logging

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)

# 콘솔에 판다스 결과값 최대 표시 설정
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

class RecentModifyUpdate:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, db='STOCKS', user='root', passwd='Lsm11875**',
                                    charset='utf8', autocommit=True)
        recent_year = self.recent_report_year()
        self.modify_update(recent_year)

    # 가장 최근 refined dir 조회
    @staticmethod
    def recent_report_year():
        root_dir = 'refined_state_files/state_year'
        root_file_list = os.listdir(root_dir)
        last_dir = root_file_list[-1]
        return last_dir

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

    # 같은 종목 코드를 가진 기업명을 최근 연도 기준으로 통일
    def modify_update(self, recent_year):
        try:
            with self.conn.cursor() as curs:
                # sql문 공부를 더 해야겠네
                # db에서 데이터를 내려받을거 없이 sql문만으로 해결?
                # 해당 종목코드칼럼, year칼럼에서 가장 큰 숫자를 기준,
                sql = f"SELECT year, code FROM company_state WHERE year={recent_year}"
                df = pd.read_sql(sql, self.conn)

                for code in df.code:
                    sql = f"SELECT code, company_nm FROM company_state WHERE code={code}"
                    df = pd.read_sql(sql, self.conn)

                    recent_comp_nm = df.company_nm.iloc[-1]

                    # 값이 어떻게 변경될지 테스트가 필요하다. 잘못 변경되도 되돌릴수 있는 장치 없을까?
                    sql = f"UPDATE company_state SET company_nm='{recent_comp_nm}' " \
                          f"WHERE code='{code}'"
                    curs.execute(sql)
                    self.conn.commit()
                    print(f"code: {code}, comp_nm: {recent_comp_nm}")
        except:
            logging.error(traceback.format_exc())
            return

    # 상장 폐지된 종목 row 삭제

if __name__ == '__main__':
    execution = RecentModifyUpdate()

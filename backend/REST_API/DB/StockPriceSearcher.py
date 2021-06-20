from REST_API.DB.Connector import connector as conn
import pandas as pd
from datetime import datetime
from datetime import timedelta
import re

# 종목 검색기 API?
class Market:
    def __init__(self):
        # 딕셔너리 초기화
        self.codes = {}
        # codes 딕셔너리에 넣을 종목코드,회사명 데이터 테이블 조회 함수
        self.get_comp_info()

    def __del__(self):
        conn.close()

    def get_comp_info(self):
        sql = "SELECT * FROM company_info"
        krx = pd.read_sql(sql, conn)

        for idx in range(len(krx)):
            self.codes[krx['code'].values[idx]] = krx['company'].values[idx]

    def get_daily_price(self, code, start_date=None, end_date=None):
        """KRX 종목의 일별 시세를 데이터프레임 형태로 반환
           - code        : KRX 종목코드('005930') 또는 상장기업명('삼성전자')
           - start_date  : 조회 시작일('2020-01-01'), 미입력 시 1년 전 오늘
           - end_date    : 조회 종료일('2020-12-31'), 미입력 시 오늘 날짜
        """

        # 인수가 입력되지 않은 경우
        if start_date is None:
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime('%Y-%m-%d')  # 1년전 오늘 날짜로 문자열 처리
            print("start_date is initialized to '{}'".format(start_date))

        else:
            start_list = re.split('\D+', start_date)  # 정규표현식 \D+ 로 분리하면 연, 월 일에 해당하는 숫자만 남게된다.
            if start_list[0] == '':
                start_list = start_list[1:]
            start_year = int(start_list[0])
            start_month = int(start_list[1])
            start_day = int(start_list[2])

            if start_year < 1900 or start_year > 2200:
                print(f"ValueError: start_year({start_year:d}) is wrong.")
                return
            if start_month < 1 or start_month > 12:
                print(f"ValueError: start_month({start_year:d}) is wrong.")
                return
            if start_day < 1 or start_day > 31:
                print(f"ValueError: start_day({start_year:d}) is wrong.")
                return
            start_date = f"{start_year:04d}-{start_month:02d}-{start_day:02d}"

        if end_date is None:
            end_date = datetime.today().strftime('%Y-%m-%d')
            print("end_date is initialized to '{}'".format(end_date))

        else:
            end_lst = re.split('\D+', end_date)
            if end_lst[0] == '':
                end_lst = end_lst[1:]
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            if end_year < 1800 or end_year > 2200:
                print(f"ValueError: end_year({end_year:d}) is wrong.")
                return
            if end_month < 1 or end_month > 12:
                print(f"ValueError: end_month({end_month:d}) is wrong.")
                return
            if end_day < 1 or end_day > 31:
                print(f"ValueError: end_day({end_day:d}) is wrong.")
                return
            end_date = f"{end_year:04d}-{end_month:02d}-{end_day:02d}"

                # codes 딕셔너리로부터 키들을 뽑아서 키(종목코드) 리스트에 존재한다면 별도의 처리 없이 그대로 사용
        codes_keys = list(self.codes.keys())
        codes_values = list(self.codes.values())

        # 사용자가 입력한 값이 키 (종목코드) 리스트에 존재한다면 별도의 처리 없이 그대로 사용
        if code in codes_keys:
            pass
        # 사용자가 입력한 값이 '회사명' 이고 리스트에 존재한다면
        elif code in codes_values:
            idx = codes_values.index(code)  # 리스트에서 '회사명'의 인덱스를 구한다.
            code = codes_keys[idx]  # 키(종목코드) 리스트에서 동일한 인덱스에 위치한 값(종목코드)을 구한다.
        else:
            print(f"ValueError: code({code}) doesn't exits.")

        sql = f"SELECT * FROM daily_price WHERE code='{code}' AND date >= '{start_date}' AND date <= '{end_date}'"
        df = pd.read_sql(sql, conn)
        df.index = df['date']
        return df

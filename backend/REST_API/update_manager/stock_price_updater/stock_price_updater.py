import traceback
import FinanceDataReader as fdr
import pandas as pd
from REST_API.update_manager.DB.Connector import conn
from datetime import datetime
import logging

import time

# 콘솔에 판다스 결과값 최대 표시 설정
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)


# 전 종목 2021년 1월 8일 부터 업데이트 시작 (code, date, open, high, low, close, diff, volume)
# IP 차단을 대비한 로직이 필요
class DailyUpdater:
    def __init__(self):
        print('Stocks price Updating')
        code_list = self.read_krx_code()
        code_list_len = len(code_list)
        progress_count = 0

        MODE_TEST = 'MODE_TEST'  # 테스트용 쿼리
        MODE_EXECUTE = 'MODE_EXECUTE'  # 자동화 가장 빠른 쿼리
        MODE_SUB_EXECUTE = 'MODE_SUB_EXECUTE'  # 자동화 조금 느리지만 정확한 서브쿼리

        for code in code_list:
            progress_count += 1

            if progress_count % 50 != 0:
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(
                    f"[{tmnow}] {progress_count :04d} / {code_list_len} ({round((progress_count / code_list_len) * 100, 2)}%) {code} (REPLACE UPDATE)")
                self.update_stock_price(code, MODE_TEST)
            else:
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(
                    f"[{tmnow}] {progress_count :04d} / {code_list_len} ({round((progress_count / code_list_len) * 100, 2)}%) {code} (REPLACE UPDATE) 1분 스크랩핑 대기")
                self.update_stock_price(code)
                time.sleep(61)

    # 현재 상장된 모든 krx 기업 코드 리턴
    @staticmethod
    def read_krx_code():
        """KRX로부터 상장법인목록 파일을 읽어와서 데이터프레임으로 반환"""
        url = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
        krx = pd.read_html(url, header=0)[0]  # [0]을 붙임으로써 결괏값을 데이터프레임으로 받는다.
        krx = krx[['종목코드', '회사명']]  # 종목코드 칼럼과 회사명만 남긴다. 데이터프레임에 [[]]을 사용하면 특정 칼럼만 뽑아서 원하는 순서대로 재구성할 수 있다.
        krx = krx.rename(columns={'종목코드': 'code', '회사명': 'company'})  # 한글 칼럼명을 영문 칼럼명으로 변경
        krx.drop(columns=["company"], axis=1, inplace=True)
        krx.code = krx['code'].map(
            '{:06d}'.format)  # krx_list[0].종목코드 = krx_list[0].종목코드.map('{:06d}'.format) # 종목코드의 앞자리 0 보정 : {:06f}는 여석 자리 숫자 형식으로 표현하되 빈 앞 자리를 0으로 채우라는 뜻
        krx.sort_values(by='code',
                        inplace=True)  # 종목코드 칼럼의 값으로 정렬, 기본은 오름차순 정렬이며, ascending=False를 인수로 추가하면 내림차순으로 정렬된다.
        return krx.code

    # 주가 데이터 취득 함수
    def stock_price(self, code, MODE):
        global select_sql, yesterday_close_price
        try:
            # 현재 년도, 월, 일을 기준으로 업데이트
            # 스케쥴러 등록, 주말, 공휴일을 제외한 당일날짜 없데이트(전일비 계산을 위해 2일치를 불러야함)
            year = datetime.today().year
            month = datetime.today().month
            date = datetime.today().day

            start = f"{year}-{month}-{date}"
            end = f"{year}-{month}-{date}"

            # 당일 연월일 기준 (스케쥴러에 공휴일을 제외한 날짜로 등록해야함)
            result_df = fdr.DataReader(code, start, end)

            # 해당 종목의 전체 날짜를 비교해야하기 때문에 로우가 길어질수록 느려질수 있다.
            # 차라리 해당 종목의 모든 종가를 가져와서 데이터프레임으로 마지막 데이터를 취득하는게 더 빠를수 있다.
            # 매번 마지막 date를 기준으로 diff를 계산하기 때문에 여러번 테스트할 수 없음. sql 문을 하드코딩하면 여러번 테스트할수 있음
            # 테스트용 쿼리
            if MODE == 'MODE_TEST':
                select_sql = f"SELECT close FROM daily_price WHERE code={code} AND date='2021-06-11';"  # 하드코딩된 날짜를 사용한 쿼리
                df = pd.read_sql(select_sql, conn)
                yesterday_close_price = df.iloc[0].close  # 테스트를 위한 하드코딩 코드

            #  가장 빠른 쿼리 : 자동화에 사용
            elif MODE == 'MODE_EXECUTE':
                select_sql = f"SELECT close FROM daily_price WHERE code={code};"  # 해당 종목의 전체 종가를 가져오는 쿼리, 지금으로썬 가장 빠름
                df = pd.read_sql(select_sql, conn)
                yesterday_close_price = df.iloc[-1].close  # DB에 저장된 전일 종가 데이터 취득.

            #  가장 정확하지만 느린 쿼리
            elif MODE == 'MODE_SUB_EXECUTE':
                select_sql = f"SELECT close FROM daily_price WHERE code={code} AND date=(SELECT MAX(date) FROM daily_price);"  # 서브쿼리 사용. 행이 길어질수록 느림
                df = pd.read_sql(select_sql, conn)
                yesterday_close_price = df.iloc[0].close  # 서브쿼리를 사용한 코드

            # index: date
            open_price = result_df.Open
            high_price = result_df.High
            low_price = result_df.Low
            close_price = result_df.Close
            volume = result_df.Volume
            diff = close_price[start] - yesterday_close_price

            result_dict = {
                'date': start,
                'open': open_price[start],
                'high': high_price[start],
                'low': low_price[start],
                'close': close_price[start],
                'volume': volume[start],
                'diff': diff
            }
            return result_dict

        except:
            logging.error(traceback.format_exc())
            return 0

    # 주가 업데이트 함수
    def update_stock_price(self, code, MODE):
        try:
            stock_df = self.stock_price(code, MODE)

            date = stock_df.get('date')
            open_price = stock_df.get('open')
            high_price = stock_df.get('high')
            low_price = stock_df.get('low')
            close_price = stock_df.get('close')
            diff = stock_df.get('diff')
            volume = stock_df.get('volume')

            with conn.cursor() as curs:
                update_sql = f"REPLACE INTO daily_price (code, date, open, high, low, close, diff, volume)" \
                      f"VALUES ('{code}', '{date}', '{open_price}', '{high_price}', '{low_price}', '{close_price}', '{diff}', '{volume}')"
                curs.execute(update_sql)
                conn.commit()

            return 1
        except:
            logging.error(traceback.format_exc())
            return -1


if __name__ == '__main__':
    execution = DailyUpdater()
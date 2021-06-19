import traceback
import FinanceDataReader as fdr
import pandas as pd
from REST_API.update_manager.DB.Connector import conn
from datetime import datetime
import logging
from multiprocessing import Pool

import time

# 콘솔에 판다스 결과값 최대 표시 설정
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)


# 전 종목 2021년 1월 8일 부터 업데이트 시작 (code, date, open, high, low, close, diff, volume)
# IP 차단을 대비한 로직이 필요
# 업데이트 못한 날짜 부터 차례로 업데이트 하는 로직으로 변경하기
class DailyUpdater:

    def __init__(self):
        print('Stocks price Updating')
        code_list = self.read_krx_code()
        code_list_len = len(code_list)
        progress_count = 0

        pool = Pool(processes=4)

        MODE_TEST = 'MODE_TEST'  # 테스트용 쿼리
        MODE_EXECUTE = 'MODE_EXECUTE'  # 자동화 가장 빠른 쿼리
        MODE_SUB_EXECUTE = 'MODE_SUB_EXECUTE'  # 자동화 조금 느리지만 정확한 서브쿼리

        # 코드순회
        for code in code_list:
            progress_count += 1
            # 마지막 업데이트 날짜 조회

            if progress_count % 100 != 0:
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(
                    f"[{tmnow}] {progress_count :04d} / {code_list_len} ({round((progress_count / code_list_len) * 100, 2)}%) {code} (REPLACE UPDATE)")
                # pool.map(func=self.test_stock_price, iterable=date_list)
                self.update_stock_price(code)
            else:
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(
                    f"[{tmnow}] {progress_count :04d} / {code_list_len} ({round((progress_count / code_list_len) * 100, 2)}%) {code} (REPLACE UPDATE) 1분 스크랩핑 대기")
                # pool.map(func=self.test_stock_price, iterable=date_list)
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
    def update_stock_price(self, code):
        global select_sql, yesterday_close_price
        try:
            # 마지막으로 업데이트된 date를 구한다
            get_date_sql = f"SELECT date FROM daily_price WHERE code={code};"
            df = pd.read_sql(get_date_sql, conn)

            today = datetime.today()
            last_update = str(df.iloc[-1].date)

            # 마지막 업데이트 날짜와 현재까지의 날짜 리스트
            date_list = pd.date_range(last_update, today).strftime('%Y-%m-%d')

            # 당일 연월일 기준 (스케쥴러에 공휴일을 제외한 날짜로 등록해야함 -> 공휴일 값은 자동으로 표시되지 않음)
            result_df = fdr.DataReader(code, date_list[0], date_list[-1])

            for idx in range(len(result_df)):
                # 주가 전일차 계산 : IndexError: single positional indexer is out-of-bounds가 발생하지만 업데이트에 문제 없음
                before_close_price = result_df.iloc[idx].Close
                next_close_price = result_df.iloc[idx+1].Close
                diff = next_close_price - before_close_price

                # datareader로 OHLCV를 취득
                # next_close_price에 맞춰서 OHLCV에 idx+1을 해서 값을 구해야 한다.
                open_price = result_df.iloc[idx+1].Open
                high_price = result_df.iloc[idx+1].High
                low_price = result_df.iloc[idx+1].Low
                close_price = result_df.iloc[idx+1].Close
                volume = result_df.iloc[idx+1].Volume
                # print(f"[{date_list[idx+1]}] 시가: {open_price} 고가: {high_price} 저가: {low_price} 종가: {close_price} 거래량: {volume} 전일차: {diff}")

                # 업데이트
                with conn.cursor() as curs:
                    update_sql = f"REPLACE INTO daily_price (code, date, open, high, low, close, diff, volume)" \
                                 f"VALUES ('{code}', '{date_list[idx+1]}', '{open_price}', '{high_price}', '{low_price}', '{close_price}', '{diff}', '{volume}')"
                    curs.execute(update_sql)
                    conn.commit()
            return
        except:
            # logging.error(traceback.format_exc())
            pass

    def test_stock_price(self, date):
        try:
            result_df = fdr.DataReader(self.code, date, date)

            print(result_df.Close.values[0])
            return
        except:
            return

    # 주가 업데이트 함수
    # def update_stock_price(self, code, MODE):
    #     try:
    #         stock_df = self.get_stock_price(code, MODE)
    #
    #         date = stock_df.get('date')
    #         open_price = stock_df.get('open')
    #         high_price = stock_df.get('high')
    #         low_price = stock_df.get('low')
    #         close_price = stock_df.get('close')
    #         diff = stock_df.get('diff')
    #         volume = stock_df.get('volume')
    #
    #         with conn.cursor() as curs:
    #             update_sql = f"REPLACE INTO daily_price (code, date, open, high, low, close, diff, volume)" \
    #                   f"VALUES ('{code}', '{date}', '{open_price}', '{high_price}', '{low_price}', '{close_price}', '{diff}', '{volume}')"
    #             curs.execute(update_sql)
    #             conn.commit()
    #
    #         return 1
    #     except:
    #         logging.error(traceback.format_exc())
    #         pass


if __name__ == '__main__':
    execution = DailyUpdater()

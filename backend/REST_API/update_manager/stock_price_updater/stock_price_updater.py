import FinanceDataReader as fdr
import pandas as pd
from REST_API.DB.Connector import connector
from REST_API.update_manager.downloader.KrxList import read_krx_code
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
# 업데이트 못한 날짜 부터 차례로 업데이트 하는 로직으로 변경하기
class DailyUpdater:

    def __init__(self):
        print('Stocks price Updating')
        code_list = read_krx_code()
        code_list_len = len(code_list)
        progress_count = 0

        # 코드순회
        for code in code_list.code:
            progress_count += 1
            # 마지막 업데이트 날짜 조회

            if progress_count % 100 != 0:
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(
                    f"[{tmnow}] {progress_count :04d} / {code_list_len} ({round((progress_count / code_list_len) * 100, 2)}%) {code} (REPLACE UPDATE)")
                self.update_stock_price(code)
            else:
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(
                    f"[{tmnow}] {progress_count :04d} / {code_list_len} ({round((progress_count / code_list_len) * 100, 2)}%) {code} (REPLACE UPDATE) 1분 스크랩핑 대기")
                self.update_stock_price(code)
                time.sleep(61)

    # DB 연결해제
    def __del__(self):
        connector.close()

    # 주가 데이터 취득 함수
    def update_stock_price(self, code):
        try:
            # 마지막으로 업데이트된 date를 구한다
            get_date_sql = f"SELECT date FROM daily_price WHERE code={code};"
            df = pd.read_sql(get_date_sql, connector)

            today = datetime.today()
            last_update = str(df.iloc[-1].date)

            # 마지막 업데이트 날짜와 현재까지의 날짜 리스트
            date_list = pd.date_range(last_update, today).strftime('%Y-%m-%d')

            # 당일 연월일 기준 (스케쥴러에 공휴일을 제외한 날짜로 등록해야함 -> 공휴일 값은 자동으로 표시되지 않음)
            result_df = fdr.DataReader(code, date_list[0], date_list[-1])

            for idx in range(len(result_df)):
                # 주가 전일차 계산 : IndexError: single positional indexer is out-of-bounds가 발생하지만 업데이트에 문제 없음
                before_close_price = result_df.iloc[idx].Close
                next_close_price = result_df.iloc[idx + 1].Close
                diff = next_close_price - before_close_price

                # datareader로 OHLCV를 취득
                # next_close_price에 맞춰서 OHLCV에 idx+1을 해서 값을 구해야 한다.
                open_price = result_df.iloc[idx + 1].Open
                high_price = result_df.iloc[idx + 1].High
                low_price = result_df.iloc[idx + 1].Low
                close_price = result_df.iloc[idx + 1].Close
                volume = result_df.iloc[idx + 1].Volume

                # 업데이트
                with connector.cursor() as curs:
                    update_sql = f"REPLACE INTO daily_price (code, date, open, high, low, close, diff, volume)" \
                                 f"VALUES ('{code}', '{date_list[idx + 1]}', '{open_price}', '{high_price}', '{low_price}', '{close_price}', '{diff}', '{volume}')"
                    curs.execute(update_sql)
                    connector.commit()
            return
        except:
            # logging.error(traceback.format_exc())
            pass


if __name__ == '__main__':
    execution = DailyUpdater()

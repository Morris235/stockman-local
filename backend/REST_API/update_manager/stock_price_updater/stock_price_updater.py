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

        for code in code_list:
            progress_count += 1

            if progress_count % 50 != 0:
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{tmnow}] {progress_count :04d} / {code_list_len} ({round((progress_count / code_list_len) * 100, 2)}%) {code} (REPLACE UPDATE)")
                self.update_stock(code)
            else:
                tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{tmnow}] {progress_count :04d} / {code_list_len} ({round((progress_count / code_list_len) * 100, 2)}%) {code} (REPLACE UPDATE) 1분 스크랩핑 대기")
                self.update_stock(code)
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
        krx.sort_values(by='code', inplace=True)  # 종목코드 칼럼의 값으로 정렬, 기본은 오름차순 정렬이며, ascending=False를 인수로 추가하면 내림차순으로 정렬된다.
        return krx.code

    def stock_price(self, code):
        try:
            # 현재 년도, 월, 일을 기준으로 업데이트, 하지만 지금은 1월 8일부터의 지금까지의 기록이 전부 필요하므로 날짜는 하드코딩한다.
            # 스케쥴러 등록, 주말, 공휴일을 제외한 당일날짜 없데이트(전일비 계산을 위해 2일치를 불러야함)
            year = datetime.today().year
            month = datetime.today().month
            date = datetime.today().day

            start = f"{year}-{month}-{date-1}"
            end = f"{year}-{month}-{date}"

            # start = f"2021-01-07"
            # end = f"2021-06-11"

            # 재무 정산일을 기준으로 날짜를 정해야 한다. (대략 각 년도별 3월 31일) : 정확한 기준 아님
            result_df = fdr.DataReader(code, start, end)

            open_price = result_df.Open
            high_price = result_df.High
            low_price = result_df.Low
            close_price = result_df.Close
            volume = result_df.Volume
            date = result_df.index.date  # 길이: 날짜수만큼


            result_dict = {
                'date': date,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            }
            return result_dict

        except:
            logging.error(traceback.format_exc())
            return 0

    def update_stock(self, code):
        try:
            stock_df = self.stock_price(code)

            date_list = stock_df.get('date')
            open_price = stock_df.get('open')
            high_price = stock_df.get('high')
            low_price = stock_df.get('low')
            close_price = stock_df.get('close')
            volume = stock_df.get('volume')


            for idx in range(len(date_list)):
                if idx > 0:
                    date = str(date_list[idx])
                    last_date = str(date_list[idx-1])

                    diff = close_price[date] - close_price[last_date]  # 전일비

                    with conn.cursor() as curs:
                        # 형식: date = 2021-01-08
                        sql = f"REPLACE INTO daily_price (code, date, open, high, low, close, diff, volume)" \
                              f"VALUES ('{code}', '{date}', '{open_price[date]}', '{high_price[date]}', '{low_price[date]}', '{close_price[date]}', '{diff}', '{volume[date]}')"
                        curs.execute(sql)
                        conn.commit()
        except:
            logging.error(traceback.format_exc())
            return

if __name__ == '__main__':
    execution = DailyUpdater()

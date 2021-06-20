# DB에 있는 전 종목의 전일비(diff) 수정 클래스. 모두 수정되면 이 클래스는 더 이상 필요가 없으므로 삭제한다. (1회용 코드)

from REST_API.DB.Connector import connector
import pandas as pd
import logging
import FinanceDataReader as fdr
import traceback

# 콘솔에 판다스 결과값 최대 표시 설정
pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

# 에러 로깅 설정
logging.basicConfig(level=logging.ERROR)


# 해당 종목의 전체 종가 필요
# db에 저장된 가장 오래된 날짜의 종가를 기준으로 그 이전의 종가를 구할수 있으면 구해서 diff를 업데이트 시키고 안되면 0으로 처리하고
# 이전날 이후날 종가를 계산해서 해당 로우의 diff 를 업데이트하는 함수

class modi_test:
    def __init__(self):
        code_list = self.read_krx_code()
        progress_count = 0

        # 전체 종목 순회
        for code in code_list:
            progress_count += 1
            self.update_close_diff(code)
            print()
            print()
        return

    # 전체 종목 diff 재계산 (+,-기호 추가)
    def update_close_diff(self, code):
        try:
            progress = 0
            # 전체 날짜를 가져오고 그 날짜 키값으로 종가를 순회하면서 diff 계산한다.
            sql = f"SELECT code, date, close FROM daily_price WHERE code={code}"
            df = pd.read_sql(sql, connector)

            for idx in range(len(df)):
                with connector.cursor() as curs:
                    before_day_close = df.iloc[idx].close
                    before_day = df.iloc[idx].date

                    next_day_close = df.iloc[idx + 1].close
                    next_day = df.iloc[idx + 1].date

                    diff = next_day_close - before_day_close

                    update_sql = f"UPDATE daily_price SET diff='{diff}' WHERE code='{code}' AND date='{next_day}'"
                    curs.execute(update_sql)
                    connector.commit()

                    print(f"[{code}] {next_day}[{next_day_close}] - {before_day}[{before_day_close}] = {diff} ")
            return
        except:
            # logging.error(traceback.format_exc())
            pass

    def get_close_price(self, code):
        try:
            # 해당 종목의 전체 종가 구함?
            with connector.cursor() as curs:
                # 해당 종목의 전체 날짜를 구하기, 구해서 첫번째부터 끝까지 종가를 구하고 전일 종가와 후일 종가를 계산하기
                # 날짜를 구해야 한다. -> db기준 마지막 종가의 이전 종가가 필요하므로. 이전 종가를 구할수 없다면 0으로 저장한다.
                date_sql = f"SELECT date FROM daily_price WHERE code={code};"
                df = pd.read_sql(date_sql, connector)
                date = df.iloc[0].date

                before_date = f"{date.year}-{date.month}-{date.day-1}"

                result_df = fdr.DataReader(code, before_date, before_date)
                # print(result_df)
                before_close_price = int(result_df.iloc[0].Close)  # db기준 첫번째 이전의 종가

                first_close_sql = f"SELECT close FROM daily_price WHERE code={code};"
                df = pd.read_sql(first_close_sql, connector)
                # print(df[:5])
                close_price = int(df.iloc[0].close)  # DB에 저장된 전일 종가 데이터 취득.
                diff = close_price - before_close_price

                print(f"({code}) [{before_date}: {before_close_price}] - [{date}: {close_price}] = {diff}")

                # 업데이트 쿼리
                update_sql = f"UPDATE daily_price SET diff='{diff}' WHERE code='{code}' AND date='{date}';"
                curs.execute(update_sql)
                connector.commit()
        except:
            logging.error(traceback.format_exc())
            pass

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

if __name__ == '__main__':
    execution = modi_test()
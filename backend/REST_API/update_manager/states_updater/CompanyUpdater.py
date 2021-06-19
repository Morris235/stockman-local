"""종목코드를 company_info 테이블에 업데이트한 후 딕셔너리에 저장 : 현재 사용 안함"""
from REST_API.update_manager.DB.Connector import connector
import pandas as pd
from datetime import datetime
from REST_API.update_manager.downloader.KrxCodeList import read_krx_code
import logging


class company_updater:
    def __init__(self):
        self.updater()

    def updater(self):
        sql = "SELECT * FROM company_info"
        df = pd.read_sql(sql, connector)  # company_info 테이블을 read_sql() 함수로 읽는다.
        codes = dict()
        for idx in range(len(df)):
            codes[df['code'].values[idx]] = df['company']  # 읽은 데이터프레임을 이용해서 종목코드와 회사명으로 codes 딕셔너리를 만든다.

        with connector.cursor() as curs:
            sql = "SELECT max(last_update) FROM company_info"
            curs.execute(sql)
            rs = curs.fetchone()  # SELECT max() ~ 구문을 이용해서 DB에서 가장 최근 업데이트 날짜를 가져온다.
            today = datetime.today().strftime('%Y-%m-%d')

            if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:  # 구한 날짜가 존재하지 않거나 오늘보다 오래된 경우에만 업데이트 한다.
                krx = read_krx_code()  # KRX 상장기업 목록 파일을 읽어서 krx 데이터프레임에 저장한다.

                for idx in range(len(krx)):
                    code = krx.code.values[idx]
                    company = krx.company.values[idx]
                    sql = f"REPLACE INTO company_info (code, company, last" \
                          f"_update) VALUES ('{code}', '{company}', '{today}')"  # f"REPLACE INTO company_info (code, company, last_update) VALUES ('{code}', '{company}', '{today}')" f-String?? 을 하지 않아서 에러 발생
                    curs.execute(sql)  # REPLACE INTO 구문을 이용해서 '종목코드,회사명,오늘날짜'행을 DB에 저장한다.
                    codes[code] = company  # codes 딕셔너리에 '키-값'으로 종목코드와 회사명을 추가한다. ex) code : company
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] {idx:04d} REPLACE INTO company_info VALUES" \
                          f" ({code}, {company}, {today})")
                connector.commit()
                print('')


if __name__ == '__main__':
    execution = company_updater()

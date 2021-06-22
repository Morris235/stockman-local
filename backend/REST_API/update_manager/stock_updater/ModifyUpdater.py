from REST_API.DB.Connector import connector
from REST_API.update_manager.downloader.KrxCompanyList import read_krx_code
import pandas as pd

krx = read_krx_code()

for code in krx.code:
    with connector.cursor() as curs:
        sql = f"DELETE FROM daily_price WHERE code='{code}' AND date='2021-06-21';"
        curs.execute(sql)
        connector.commit()
        print(f"{code} 처리 완료")

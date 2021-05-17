

# 시가총액, 시가, 발행주식수같은 업데이트가 비교적 자주 일어나야 하는 비율지표를 다른 지표 업데이트와 따로 내어내어 개별 업데이트 한다.
import OpenDartReader
import FinanceDataReader as fdr
import pykrx

# class-----------------------


# init-------------------------
# 보고서 타입
# REPORT_CODE = 11011  # 연간 보고서
# year = format(datetime.today().year)

# FinanceDataReader: 해당 기업의 현재 시가만 조회하면 되기 때문에 시작일과 종료일이 같음
# start = str(datetime(year=int(year), month=int(month), day=int(date) - 1))
# end = start

# api_key = '1df1a3c433cb50c187e45bb35461f17a5c28f255'
# dart = OpenDartReader(api_key)

# small = dart.report(krx.code.values[idx], '소액주주', year, reprt_code=REPORT_CODE)  # 총발행주식수
# 기업의 현재 시가 조회
# self.open_price = self.get_stock_price(code, start, end)


# function-------------------------
# 시가 조회 : 시장이 아직 열리지 않았다면 현재주가를 받아올수 없다
# def get_stock_price(code: str, start_year: str, end_year: str):
#     df = fdr.DataReader(code, start_year, end_year)
#     open_price = df['Open'].values[0]
#     return open_price

# 주가 순자산배율 -확인
# def pbr():
#     # 주가 / bps((총자산-총부채 ) / 총발행주식수)
#     # 주가 / 주당순자산가치
#     try:
#         return
#     except:
#         return 0.0

# # 주당순자산 -확인
# def bps_cal():
#     # 순자산 / 주식수
#     return ''

# 주당순이익 (보고서에서 바로 구할수 있으나, 없을경우 계산하기) -좀더 확인 필요
# def eps_cal():
#     # 당기 순이익 / 총발행주식수 * 100
#     # 주가 / per * 100 = 주가 / 발행주식수 * 100
#     try:
#         return
#     except:
#         return 0.0

# 주당 수익비율 -확인
# 별도는 연결과 달리 지배주주와 비지배주주 구분이 없다.
# 따라서 당기 순이익을 찾아 PER을 구하면 된다.
# 하지만 연결의 경우 지배와 비지배 당기순이익을 구분지어서 계산을 해야 한다.
# def per():
#     # 주가 / 주당 순이익(eps) * 100
#     try:
#         return
#     except:
#         return 0.0